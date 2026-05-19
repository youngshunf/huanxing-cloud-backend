from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnEnterprise
from backend.app.hasn.schema.hasn_enterprise import CreateHasnEnterpriseParam, UpdateHasnEnterpriseParam


class CRUDHasnEnterprise(CRUDPlus[HasnEnterprise]):
    async def get(self, db: AsyncSession, pk: int) -> HasnEnterprise | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnEnterprise]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnEnterpriseParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnEnterpriseParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_enterprise_dao: CRUDHasnEnterprise = CRUDHasnEnterprise(HasnEnterprise)
