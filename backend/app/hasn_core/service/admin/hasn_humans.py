"""HASN 用户管理端 Service"""
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.admin.hasn_humans import hasn_humans_admin_dao
from backend.app.hasn_core.model import HasnHuman
from backend.app.hasn_core.schema.admin.hasn_humans import CreateHasnHumanParam, DeleteHasnHumanParam, UpdateHasnHumanParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnHumanAdminService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: str) -> HasnHuman:
        obj = await hasn_humans_admin_dao.get(db, pk)
        if not obj:
            raise errors.NotFoundError(msg='用户不存在')
        return obj

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await hasn_humans_admin_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnHumanParam) -> None:
        await hasn_humans_admin_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: str, obj: UpdateHasnHumanParam) -> int:
        return await hasn_humans_admin_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnHumanParam) -> int:
        return await hasn_humans_admin_dao.delete(db, obj.pks)


hasn_humans_admin_service: HasnHumanAdminService = HasnHumanAdminService()
