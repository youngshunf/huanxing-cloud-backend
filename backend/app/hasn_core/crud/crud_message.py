"""HASN Message CRUD"""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_messages import HasnMessage


class CRUDHasnMessage:

    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> HasnMessage:
        obj = HasnMessage(**kwargs)
        db.add(obj)
        await db.flush()
        return obj

    @staticmethod
    async def get_by_conversation(
        db: AsyncSession,
        conversation_id: str,
        before_id: int | None = None,
        limit: int = 50,
    ) -> list[HasnMessage]:
        stmt = (
            select(HasnMessage)
            .where(HasnMessage.conversation_id == conversation_id)
        )
        if before_id is not None:
            stmt = stmt.where(HasnMessage.id < before_id)
        stmt = stmt.order_by(HasnMessage.id.desc()).limit(limit)
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_undelivered(db: AsyncSession, conversation_id: str) -> list[HasnMessage]:
        """获取未送达消息 (status=1)"""
        return (await db.execute(
            select(HasnMessage)
            .where(HasnMessage.conversation_id == conversation_id)
            .where(HasnMessage.status == 1)
            .order_by(HasnMessage.id.asc())
        )).scalars().all()

    @staticmethod
    async def mark_delivered(db: AsyncSession, msg_id: int) -> None:
        await db.execute(
            update(HasnMessage)
            .where(HasnMessage.id == msg_id)
            .values(status=2)
        )

    @staticmethod
    async def mark_read(db: AsyncSession, conversation_id: str, up_to_id: int) -> None:
        """标记已读: 该会话中 id <= up_to_id 的所有消息"""
        await db.execute(
            update(HasnMessage)
            .where(HasnMessage.conversation_id == conversation_id)
            .where(HasnMessage.id <= up_to_id)
            .where(HasnMessage.status < 3)
            .values(status=3)
        )


crud_hasn_message = CRUDHasnMessage()
