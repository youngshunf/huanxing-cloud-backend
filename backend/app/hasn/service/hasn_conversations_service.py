from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_conversations import hasn_conversations_dao
from backend.app.hasn.model import HasnConversations
from backend.app.hasn.schema.hasn_conversations import CreateHasnConversationsParam, DeleteHasnConversationsParam, UpdateHasnConversationsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnConversationsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnConversations:
        """
        获取HASN 会话

        :param db: 数据库会话
        :param pk: HASN 会话 ID
        :return:
        """
        hasn_conversations = await hasn_conversations_dao.get(db, pk)
        if not hasn_conversations:
            raise errors.NotFoundError(msg='HASN 会话不存在')
        return hasn_conversations

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN 会话列表

        :param db: 数据库会话
        :return:
        """
        hasn_conversations_select = await hasn_conversations_dao.get_select()
        return await paging_data(db, hasn_conversations_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnConversations]:
        """
        获取所有HASN 会话

        :param db: 数据库会话
        :return:
        """
        hasn_conversationss = await hasn_conversations_dao.get_all(db)
        return hasn_conversationss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnConversationsParam) -> None:
        """
        创建HASN 会话

        :param db: 数据库会话
        :param obj: 创建HASN 会话参数
        :return:
        """
        await hasn_conversations_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnConversationsParam) -> int:
        """
        更新HASN 会话

        :param db: 数据库会话
        :param pk: HASN 会话 ID
        :param obj: 更新HASN 会话参数
        :return:
        """
        count = await hasn_conversations_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnConversationsParam) -> int:
        """
        删除HASN 会话

        :param db: 数据库会话
        :param obj: HASN 会话 ID 列表
        :return:
        """
        count = await hasn_conversations_dao.delete(db, obj.pks)
        return count


hasn_conversations_service: HasnConversationsService = HasnConversationsService()
