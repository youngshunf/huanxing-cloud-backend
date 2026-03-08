"""HASN 消息管理端 CRUD"""
from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn_core.model import HasnMessage
from backend.app.hasn_core.schema.admin.hasn_messages import CreateHasnMessageParam, UpdateHasnMessageParam


class CRUDHasnMessageAdmin(CRUDPlus[HasnMessage]):
    async def get(self, db: AsyncSession, pk: int) -> HasnMessage | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnMessage]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnMessageParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnMessageParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_messages_admin_dao: CRUDHasnMessageAdmin = CRUDHasnMessageAdmin(HasnMessage)
