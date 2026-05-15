from typing import Any, Sequence
import uuid

from sqlalchemy import select
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

    @staticmethod
    async def ensure_conversation(
        *,
        db: AsyncSession,
        caller_hasn_id: str,
        peer_hasn_id: str,
        relation_type: str = 'social',
    ) -> HasnConversations:
        """
        确保会话存在（如果不存在则创建）

        用于 1:1 会话的幂等创建。根据排序后的参与者对查找或创建会话。

        :param db: 数据库会话
        :param caller_hasn_id: 调用者的 HASN ID
        :param peer_hasn_id: 对方的 HASN ID
        :param relation_type: 关系类型，默认 'social'
        :return: 会话对象
        """
        # 对参与者 ID 排序，确保同一对用户总是得到相同的会话
        participant_a, participant_b = sorted([caller_hasn_id, peer_hasn_id])

        # 确定参与者类型（h_ 开头是 human，a_ 开头是 agent）
        def get_participant_type(hasn_id: str) -> str:
            if hasn_id.startswith('h_'):
                return 'human'
            elif hasn_id.startswith('a_'):
                return 'agent'
            else:
                raise errors.BadRequestError(msg=f'无效的 HASN ID 格式: {hasn_id}')

        participant_a_type = get_participant_type(participant_a)
        participant_b_type = get_participant_type(participant_b)

        # 查找现有会话
        stmt = select(HasnConversations).where(
            HasnConversations.type == 'direct',
            HasnConversations.participant_a_id == participant_a,
            HasnConversations.participant_b_id == participant_b,
        )
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()

        if conversation:
            return conversation

        # 创建新会话
        new_conversation = HasnConversations(
            type='direct',
            relation_type=relation_type,
            participant_a_id=participant_a,
            participant_b_id=participant_b,
            participant_a_type=participant_a_type,
            participant_b_type=participant_b_type,
            agent_policy='free',
            join_policy='',
            max_members=2,
            allow_invite=False,
            mute_all=False,
            member_count=2,
            message_count=0,
            status='active',
        )
        db.add(new_conversation)
        await db.flush()
        await db.refresh(new_conversation)

        return new_conversation


hasn_conversations_service: HasnConversationsService = HasnConversationsService()
