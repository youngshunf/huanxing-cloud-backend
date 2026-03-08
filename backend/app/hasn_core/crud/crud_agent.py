"""HASN Agent CRUD"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_agents import HasnAgent


class CRUDHasnAgent:

    @staticmethod
    async def get_by_id(db: AsyncSession, hasn_id: str) -> HasnAgent | None:
        return (await db.execute(
            select(HasnAgent).where(HasnAgent.id == hasn_id)
        )).scalars().first()

    @staticmethod
    async def get_by_star_id(db: AsyncSession, star_id: str) -> HasnAgent | None:
        return (await db.execute(
            select(HasnAgent).where(HasnAgent.star_id == star_id)
        )).scalars().first()

    @staticmethod
    async def get_by_owner_id(db: AsyncSession, owner_id: str) -> list[HasnAgent]:
        return (await db.execute(
            select(HasnAgent)
            .where(HasnAgent.owner_id == owner_id)
            .where(HasnAgent.status == 'active')
        )).scalars().all()

    @staticmethod
    async def get_by_api_key_hash(db: AsyncSession, key_hash: str) -> HasnAgent | None:
        return (await db.execute(
            select(HasnAgent).where(HasnAgent.api_key_hash == key_hash)
        )).scalars().first()

    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> HasnAgent:
        obj = HasnAgent(**kwargs)
        db.add(obj)
        await db.flush()
        return obj


crud_hasn_agent = CRUDHasnAgent()
