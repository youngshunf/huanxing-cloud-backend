"""HASN 会话管理端 Service"""
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.admin.hasn_conversations import hasn_conversations_admin_dao
from backend.app.hasn_core.model import HasnConversation
from backend.app.hasn_core.schema.admin.hasn_conversations import CreateHasnConversationParam, DeleteHasnConversationParam, UpdateHasnConversationParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnConversationAdminService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: str) -> HasnConversation:
        obj = await hasn_conversations_admin_dao.get(db, pk)
        if not obj:
            raise errors.NotFoundError(msg='会话不存在')
        return obj

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await hasn_conversations_admin_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnConversationParam) -> None:
        await hasn_conversations_admin_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: str, obj: UpdateHasnConversationParam) -> int:
        return await hasn_conversations_admin_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnConversationParam) -> int:
        return await hasn_conversations_admin_dao.delete(db, obj.pks)


hasn_conversations_admin_service: HasnConversationAdminService = HasnConversationAdminService()
