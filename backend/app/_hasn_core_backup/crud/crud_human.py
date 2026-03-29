"""HASN Human 业务查询 CRUD（contacts 兼容层）"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.model.hasn_humans import HasnHumans


class CRUDHasnHuman:
    @staticmethod
    async def get_by_id(db: AsyncSession, hasn_id: str) -> HasnHumans | None:
        result = await db.execute(select(HasnHumans).where(HasnHumans.hasn_id == hasn_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_star_id(db: AsyncSession, star_id: str) -> HasnHumans | None:
        result = await db.execute(select(HasnHumans).where(HasnHumans.star_id == star_id))
        return result.scalar_one_or_none()


crud_hasn_human = CRUDHasnHuman()
