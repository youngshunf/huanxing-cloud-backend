import uuid
from datetime import timedelta
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_node_bindings import hasn_node_bindings_dao
from backend.app.hasn.model import HasnNodeBindings
from backend.app.hasn.schema.hasn_node_bindings import CreateHasnNodeBindingsParam, DeleteHasnNodeBindingsParam, UpdateHasnNodeBindingsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone


class HasnNodeBindingsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnNodeBindings:
        """
        获取HASN Node Owner Binding 租约

        :param db: 数据库会话
        :param pk: HASN Node Owner Binding 租约 ID
        :return:
        """
        hasn_node_bindings = await hasn_node_bindings_dao.get(db, pk)
        if not hasn_node_bindings:
            raise errors.NotFoundError(msg='HASN Node Owner Binding 租约不存在')
        return hasn_node_bindings

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN Node Owner Binding 租约列表

        :param db: 数据库会话
        :return:
        """
        hasn_node_bindings_select = await hasn_node_bindings_dao.get_select()
        return await paging_data(db, hasn_node_bindings_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnNodeBindings]:
        """
        获取所有HASN Node Owner Binding 租约

        :param db: 数据库会话
        :return:
        """
        hasn_node_bindingss = await hasn_node_bindings_dao.get_all(db)
        return hasn_node_bindingss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnNodeBindingsParam) -> None:
        """
        创建HASN Node Owner Binding 租约

        :param db: 数据库会话
        :param obj: 创建HASN Node Owner Binding 租约参数
        :return:
        """
        await hasn_node_bindings_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnNodeBindingsParam) -> int:
        """
        更新HASN Node Owner Binding 租约

        :param db: 数据库会话
        :param pk: HASN Node Owner Binding 租约 ID
        :param obj: 更新HASN Node Owner Binding 租约参数
        :return:
        """
        count = await hasn_node_bindings_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnNodeBindingsParam) -> int:
        """
        删除HASN Node Owner Binding 租约

        :param db: 数据库会话
        :param obj: HASN Node Owner Binding 租约 ID 列表
        :return:
        """
        count = await hasn_node_bindings_dao.delete(db, obj.pks)
        return count

    @staticmethod
    async def get_active_binding(*, db: AsyncSession, node_id: str, owner_id: str) -> HasnNodeBindings | None:
        result = await db.execute(
            select(HasnNodeBindings).where(
                HasnNodeBindings.node_id == node_id,
                HasnNodeBindings.owner_id == owner_id,
                HasnNodeBindings.status == 'active',
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def add_owner_binding(
        *,
        db: AsyncSession,
        node_id: str,
        owner_id: str,
        auth_profile: str,
        scopes: dict | None = None,
        expires_at=None,
    ) -> HasnNodeBindings:
        existing = await HasnNodeBindingsService.get_active_binding(db=db, node_id=node_id, owner_id=owner_id)
        if existing:
            return existing

        if expires_at is None:
            expires_at = timezone.now() + timedelta(days=30)

        binding = HasnNodeBindings(
            binding_id=f"ob_{uuid.uuid4().hex[:12]}",
            node_id=node_id,
            owner_id=owner_id,
            auth_profile=auth_profile,
            scopes=scopes or {'bind_owner': True, 'register_agent': True},
            status='active',
            bound_at=timezone.now(),
            expires_at=expires_at,
            last_used_at=timezone.now(),
        )
        db.add(binding)
        await db.flush()
        return binding

    @staticmethod
    async def renew_owner_binding(
        *,
        db: AsyncSession,
        node_id: str,
        owner_id: str,
        expires_at,
    ) -> HasnNodeBindings:
        binding = await HasnNodeBindingsService.get_active_binding(db=db, node_id=node_id, owner_id=owner_id)
        if not binding:
            raise errors.NotFoundError(msg='Owner Binding 不存在')
        binding.expires_at = expires_at or (timezone.now() + timedelta(days=30))
        binding.renewed_at = timezone.now()
        binding.last_used_at = timezone.now()
        await db.flush()
        return binding

    @staticmethod
    async def remove_owner_binding(*, db: AsyncSession, node_id: str, owner_id: str) -> bool:
        binding = await HasnNodeBindingsService.get_active_binding(db=db, node_id=node_id, owner_id=owner_id)
        if not binding:
            return False
        binding.status = 'removed'
        binding.updated_time = timezone.now()
        await db.flush()
        return True

    @staticmethod
    async def list_active_bindings(*, db: AsyncSession, node_id: str) -> Sequence[HasnNodeBindings]:
        result = await db.execute(
            select(HasnNodeBindings).where(
                HasnNodeBindings.node_id == node_id,
                HasnNodeBindings.status == 'active',
            ).order_by(HasnNodeBindings.created_time.desc())
        )
        return result.scalars().all()


hasn_node_bindings_service: HasnNodeBindingsService = HasnNodeBindingsService()
