from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnUserActiveWorkspace
from backend.app.hasn.schema.hasn_user_active_workspace import (
    CreateHasnUserActiveWorkspaceParam,
    UpdateHasnUserActiveWorkspaceParam,
)


class CRUDHasnUserActiveWorkspace(CRUDPlus[HasnUserActiveWorkspace]):
    async def get(self, db: AsyncSession, pk: int) -> HasnUserActiveWorkspace | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('user_id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnUserActiveWorkspace]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnUserActiveWorkspaceParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnUserActiveWorkspaceParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, user_id__in=pks)


hasn_user_active_workspace_dao: CRUDHasnUserActiveWorkspace = CRUDHasnUserActiveWorkspace(HasnUserActiveWorkspace)
