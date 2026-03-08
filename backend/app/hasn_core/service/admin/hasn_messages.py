"""HASN 消息管理端 Service"""
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.admin.hasn_messages import hasn_messages_admin_dao
from backend.app.hasn_core.model import HasnMessage
from backend.app.hasn_core.schema.admin.hasn_messages import CreateHasnMessageParam, DeleteHasnMessageParam, UpdateHasnMessageParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnMessageAdminService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnMessage:
        obj = await hasn_messages_admin_dao.get(db, pk)
        if not obj:
            raise errors.NotFoundError(msg='消息不存在')
        return obj

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await hasn_messages_admin_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnMessageParam) -> None:
        await hasn_messages_admin_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnMessageParam) -> int:
        return await hasn_messages_admin_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnMessageParam) -> int:
        return await hasn_messages_admin_dao.delete(db, obj.pks)


hasn_messages_admin_service: HasnMessageAdminService = HasnMessageAdminService()
