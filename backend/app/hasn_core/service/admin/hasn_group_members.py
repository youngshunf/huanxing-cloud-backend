"""HASN 群成员管理端 Service"""
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.admin.hasn_group_members import hasn_group_members_admin_dao
from backend.app.hasn_core.model import HasnGroupMember
from backend.app.hasn_core.schema.admin.hasn_group_members import CreateHasnGroupMemberParam, DeleteHasnGroupMemberParam, UpdateHasnGroupMemberParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnGroupMemberAdminService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnGroupMember:
        obj = await hasn_group_members_admin_dao.get(db, pk)
        if not obj:
            raise errors.NotFoundError(msg='群成员不存在')
        return obj

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await hasn_group_members_admin_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnGroupMemberParam) -> None:
        await hasn_group_members_admin_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnGroupMemberParam) -> int:
        return await hasn_group_members_admin_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnGroupMemberParam) -> int:
        return await hasn_group_members_admin_dao.delete(db, obj.pks)


hasn_group_members_admin_service: HasnGroupMemberAdminService = HasnGroupMemberAdminService()
