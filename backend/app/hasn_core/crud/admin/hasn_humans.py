"""HASN 用户管理端 CRUD"""
from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn_core.model import HasnHuman
from backend.app.hasn_core.schema.admin.hasn_humans import CreateHasnHumanParam, UpdateHasnHumanParam


class CRUDHasnHumanAdmin(CRUDPlus[HasnHuman]):
    async def get(self, db: AsyncSession, pk: str) -> HasnHuman | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnHuman]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnHumanParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: str, obj: UpdateHasnHumanParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[str]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_humans_admin_dao: CRUDHasnHumanAdmin = CRUDHasnHumanAdmin(HasnHuman)
