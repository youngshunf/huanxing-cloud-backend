"""HASN 消息业务 CRUD（socketio 兼容层）"""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_messages import HasnMessages
from backend.utils.timezone import timezone


class CRUDHasnMessage:
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> HasnMessages:
        msg = HasnMessages(**kwargs, server_received_at=timezone.now())
        db.add(msg)
        await db.flush()
        return msg

    @staticmethod
    async def mark_read(db: AsyncSession, conversation_id, last_msg_id: int) -> None:
        await db.execute(
            update(HasnMessages)
            .where(HasnMessages.conversation_id == conversation_id)
            .where(HasnMessages.id <= last_msg_id)
            .where(HasnMessages.status < 3)
            .values(status=3)
        )


crud_hasn_message = CRUDHasnMessage()
