"""HASN 会话业务 CRUD（socketio 兼容层）"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_conversations import HasnConversations
from backend.utils.timezone import timezone


class CRUDHasnConversation:
    @staticmethod
    async def get_or_create_direct(db: AsyncSession, from_id: str, to_id: str) -> HasnConversations:
        a_id, b_id = (from_id, to_id) if from_id < to_id else (to_id, from_id)
        result = await db.execute(
            select(HasnConversations).where(
                HasnConversations.type == 'direct',
                HasnConversations.participant_a_id == a_id,
                HasnConversations.participant_b_id == b_id,
            )
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv
        a_type = 'human' if a_id.startswith('h_') else 'agent'
        b_type = 'human' if b_id.startswith('h_') else 'agent'
        conv = HasnConversations(
            participant_a_id=a_id,
            participant_a_type=a_type,
            participant_b_id=b_id,
            participant_b_type=b_type,
        )
        db.add(conv)
        await db.flush()
        return conv

    @staticmethod
    async def update_last_message(db: AsyncSession, conv_id, preview: str) -> None:
        conv = await db.get(HasnConversations, conv_id)
        if conv:
            conv.last_message_preview = preview[:200]
            conv.last_message_at = timezone.now()


crud_hasn_conversation = CRUDHasnConversation()
