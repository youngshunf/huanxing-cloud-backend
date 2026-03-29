from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnHumans
from backend.app.hasn.schema.hasn_humans import CreateHasnHumansParam, UpdateHasnHumansParam


class CRUDHasnHumans(CRUDPlus[HasnHumans]):
    async def get(self, db: AsyncSession, pk: int) -> HasnHumans | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnHumans]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnHumansParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnHumansParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    # ─── 业务查询方法 ───

    @staticmethod
    async def get_by_hasn_id(db: AsyncSession, hasn_id: str) -> HasnHumans | None:
        return (await db.execute(
            select(HasnHumans).where(HasnHumans.hasn_id == hasn_id)
        )).scalars().first()

    @staticmethod
    async def get_by_star_id(db: AsyncSession, star_id: str) -> HasnHumans | None:
        return (await db.execute(
            select(HasnHumans).where(HasnHumans.star_id == star_id)
        )).scalars().first()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> HasnHumans | None:
        return (await db.execute(
            select(HasnHumans).where(HasnHumans.user_id == user_id)
        )).scalars().first()


hasn_humans_dao: CRUDHasnHumans = CRUDHasnHumans(HasnHumans)
