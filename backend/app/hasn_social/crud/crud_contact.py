"""HASN Contact CRUD (三维权限矩阵)"""
from sqlalchemy import select, update, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_social.model.hasn_contacts import HasnContact


class CRUDHasnContact:

    @staticmethod
    async def get_relation(
        db: AsyncSession,
        owner_id: str,
        peer_id: str,
        relation_type: str = 'social',
    ) -> HasnContact | None:
        """查询单条关系"""
        return (await db.execute(
            select(HasnContact)
            .where(HasnContact.owner_id == owner_id)
            .where(HasnContact.peer_id == peer_id)
            .where(HasnContact.relation_type == relation_type)
        )).scalars().first()

    @staticmethod
    async def get_all_relations(
        db: AsyncSession,
        owner_id: str,
        peer_id: str,
    ) -> list[HasnContact]:
        """查询两人之间所有类型的关系"""
        return (await db.execute(
            select(HasnContact)
            .where(HasnContact.owner_id == owner_id)
            .where(HasnContact.peer_id == peer_id)
        )).scalars().all()

    @staticmethod
    async def get_bidirectional(
        db: AsyncSession,
        id_a: str,
        id_b: str,
        relation_type: str = 'social',
    ) -> HasnContact | None:
        """双向查询: A→B 或 B→A，只要一方有关系就返回"""
        return (await db.execute(
            select(HasnContact)
            .where(HasnContact.relation_type == relation_type)
            .where(
                or_(
                    and_(HasnContact.owner_id == id_a, HasnContact.peer_id == id_b),
                    and_(HasnContact.owner_id == id_b, HasnContact.peer_id == id_a),
                )
            )
        )).scalars().first()

    @staticmethod
    async def list_contacts(
        db: AsyncSession,
        owner_id: str,
        relation_type: str | None = None,
        status: str = 'connected',
        limit: int = 50,
        offset: int = 0,
    ) -> list[HasnContact]:
        """获取联系人列表"""
        stmt = (
            select(HasnContact)
            .where(HasnContact.owner_id == owner_id)
            .where(HasnContact.status == status)
        )
        if relation_type:
            stmt = stmt.where(HasnContact.relation_type == relation_type)
        stmt = stmt.order_by(HasnContact.last_interaction_at.desc().nullslast()).offset(offset).limit(limit)
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_pending_requests(
        db: AsyncSession,
        peer_id: str,
        limit: int = 20,
    ) -> list[HasnContact]:
        """获取收到的待处理好友请求"""
        return (await db.execute(
            select(HasnContact)
            .where(HasnContact.peer_id == peer_id)
            .where(HasnContact.status == 'pending')
            .where(HasnContact.relation_type == 'social')
            .order_by(HasnContact.created_time.desc())
            .limit(limit)
        )).scalars().all()

    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> HasnContact:
        obj = HasnContact(**kwargs)
        db.add(obj)
        await db.flush()
        return obj

    @staticmethod
    async def accept_request(
        db: AsyncSession,
        contact_id: int,
    ) -> None:
        """接受好友请求: 更新状态 + 设置 connected_at"""
        await db.execute(
            update(HasnContact)
            .where(HasnContact.id == contact_id)
            .values(status='connected', trust_level=2, connected_at=func.now())
        )

    @staticmethod
    async def reject_request(
        db: AsyncSession,
        contact_id: int,
    ) -> None:
        await db.execute(
            update(HasnContact)
            .where(HasnContact.id == contact_id)
            .values(status='archived')
        )

    @staticmethod
    async def update_trust_level(
        db: AsyncSession,
        contact_id: int,
        trust_level: int,
    ) -> None:
        await db.execute(
            update(HasnContact)
            .where(HasnContact.id == contact_id)
            .values(trust_level=trust_level)
        )

    @staticmethod
    async def block(
        db: AsyncSession,
        contact_id: int,
    ) -> None:
        await db.execute(
            update(HasnContact)
            .where(HasnContact.id == contact_id)
            .values(status='blocked', trust_level=0)
        )


crud_hasn_contact = CRUDHasnContact()
