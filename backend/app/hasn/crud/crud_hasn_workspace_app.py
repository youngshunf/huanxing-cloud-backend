from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnWorkspaceApp
from backend.app.hasn.schema.hasn_workspace_app import CreateHasnWorkspaceAppParam, UpdateHasnWorkspaceAppParam


class CRUDHasnWorkspaceApp(CRUDPlus[HasnWorkspaceApp]):
    async def get(self, db: AsyncSession, pk: int) -> HasnWorkspaceApp | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnWorkspaceApp]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnWorkspaceAppParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnWorkspaceAppParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_workspace_app_dao: CRUDHasnWorkspaceApp = CRUDHasnWorkspaceApp(HasnWorkspaceApp)
