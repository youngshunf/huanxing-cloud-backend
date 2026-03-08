"""HASN Conversation CRUD"""
from uuid import uuid4

from sqlalchemy import select, update, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_conversations import HasnConversation


class CRUDHasnConversation:

    @staticmethod
    async def get_by_id(db: AsyncSession, conv_id: str) -> HasnConversation | None:
        return (await db.execute(
            select(HasnConversation).where(HasnConversation.id == conv_id)
        )).scalars().first()

    @staticmethod
    async def get_or_create_direct(
        db: AsyncSession,
        participant_a: str,
        participant_b: str,
    ) -> HasnConversation:
        """获取或创建 1v1 对话（确保 A→B 和 B→A 是同一个对话）"""
        # 标准化顺序: 小的放 a，大的放 b
        pa, pb = (min(participant_a, participant_b),
                  max(participant_a, participant_b))

        stmt = (
            select(HasnConversation)
            .where(HasnConversation.type == 'direct')
            .where(HasnConversation.participant_a == pa)
            .where(HasnConversation.participant_b == pb)
        )
        conv = (await db.execute(stmt)).scalars().first()
        if conv:
            return conv

        conv = HasnConversation(
            id=str(uuid4()),
            type='direct',
            participant_a=pa,
            participant_b=pb,
        )
        db.add(conv)
        await db.flush()
        return conv

    @staticmethod
    async def list_for_user(
        db: AsyncSession,
        hasn_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[HasnConversation]:
        """获取用户参与的所有会话，按最后消息时间倒序"""
        stmt = (
            select(HasnConversation)
            .where(
                or_(
                    HasnConversation.participant_a == hasn_id,
                    HasnConversation.participant_b == hasn_id,
                )
            )
            .where(HasnConversation.status == 'active')
            .order_by(HasnConversation.last_message_at.desc().nullslast())
            .offset(offset)
            .limit(limit)
        )
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def update_last_message(
        db: AsyncSession,
        conv_id: str,
        preview: str,
    ) -> None:
        await db.execute(
            update(HasnConversation)
            .where(HasnConversation.id == conv_id)
            .values(
                last_message_at=func.now(),
                last_message_preview=preview[:200] if preview else None,
                message_count=HasnConversation.message_count + 1,
            )
        )


crud_hasn_conversation = CRUDHasnConversation()
