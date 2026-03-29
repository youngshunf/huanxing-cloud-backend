"""HASN Agent 业务查询 CRUD（socketio / contacts 兼容层）"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_agents import HasnAgents


class CRUDHasnAgent:
    @staticmethod
    async def get_by_id(db: AsyncSession, hasn_id: str) -> HasnAgents | None:
        result = await db.execute(select(HasnAgents).where(HasnAgents.hasn_id == hasn_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_star_id(db: AsyncSession, star_id: str) -> HasnAgents | None:
        result = await db.execute(select(HasnAgents).where(HasnAgents.star_id == star_id))
        return result.scalar_one_or_none()


crud_hasn_agent = CRUDHasnAgent()
