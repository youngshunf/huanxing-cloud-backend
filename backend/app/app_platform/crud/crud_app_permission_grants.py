from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppPermissionGrants
from backend.app.app_platform.schema.app_permission_grants import CreateAppPermissionGrantsParam, UpdateAppPermissionGrantsParam


class CRUDAppPermissionGrants(CRUDPlus[AppPermissionGrants]):
    async def get(self, db: AsyncSession, pk: int) -> AppPermissionGrants | None:
        """
        获取权限授予记录

        :param db: 数据库会话
        :param pk: 权限授予记录 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取权限授予记录列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppPermissionGrants]:
        """
        获取所有权限授予记录

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppPermissionGrantsParam) -> AppPermissionGrants:
        """
        创建权限授予记录

        :param db: 数据库会话
        :param obj: 创建权限授予记录参数
        :return:
        """
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppPermissionGrantsParam) -> int:
        """
        更新权限授予记录

        :param db: 数据库会话
        :param pk: 权限授予记录 ID
        :param obj: 更新 权限授予记录参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除权限授予记录

        :param db: 数据库会话
        :param pks: 权限授予记录 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_installation_and_scope(
        self,
        db: AsyncSession,
        installation_id: str,
        scope: str,
    ) -> AppPermissionGrants | None:
        """
        根据 installation_id 和 scope 获取权限授予记录

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param scope: 权限标识
        :return:
        """
        return await self.select_model_by_column(
            db,
            installation_id=installation_id,
            scope=scope,
        )


app_permission_grants_dao: CRUDAppPermissionGrants = CRUDAppPermissionGrants(AppPermissionGrants)
