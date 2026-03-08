"""HASN Agent管理端 CRUD"""
from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn_core.model import HasnAgent
from backend.app.hasn_core.schema.admin.hasn_agents import CreateHasnAgentParam, UpdateHasnAgentParam


class CRUDHasnAgentAdmin(CRUDPlus[HasnAgent]):
    async def get(self, db: AsyncSession, pk: str) -> HasnAgent | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnAgent]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnAgentParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: str, obj: UpdateHasnAgentParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[str]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_agents_admin_dao: CRUDHasnAgentAdmin = CRUDHasnAgentAdmin(HasnAgent)
