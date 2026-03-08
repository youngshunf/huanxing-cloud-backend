"""HASN Human CRUD"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_humans import HasnHuman


class CRUDHasnHuman:

    @staticmethod
    async def get_by_id(db: AsyncSession, hasn_id: str) -> HasnHuman | None:
        return (await db.execute(
            select(HasnHuman).where(HasnHuman.id == hasn_id)
        )).scalars().first()

    @staticmethod
    async def get_by_star_id(db: AsyncSession, star_id: str) -> HasnHuman | None:
        return (await db.execute(
            select(HasnHuman).where(HasnHuman.star_id == star_id)
        )).scalars().first()

    @staticmethod
    async def get_by_huanxing_user_id(db: AsyncSession, user_id: str) -> HasnHuman | None:
        return (await db.execute(
            select(HasnHuman).where(HasnHuman.huanxing_user_id == user_id)
        )).scalars().first()

    @staticmethod
    async def get_by_phone_hash(db: AsyncSession, phone_hash: str) -> HasnHuman | None:
        return (await db.execute(
            select(HasnHuman).where(HasnHuman.phone_hash == phone_hash)
        )).scalars().first()

    @staticmethod
    async def search_by_name(db: AsyncSession, name: str, limit: int = 10) -> list[HasnHuman]:
        return (await db.execute(
            select(HasnHuman)
            .where(HasnHuman.name.ilike(f'%{name}%'))
            .where(HasnHuman.status == 'active')
            .limit(limit)
        )).scalars().all()

    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> HasnHuman:
        obj = HasnHuman(**kwargs)
        db.add(obj)
        await db.flush()
        return obj


crud_hasn_human = CRUDHasnHuman()
