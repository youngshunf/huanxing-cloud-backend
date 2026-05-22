from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn.model import HasnAiNativeAppAudit
from backend.app.hasn.schema.ai_native_audit import CreateAiNativeAppAuditParam, UpdateAiNativeAppAuditParam


class CRUDHasnAiNativeAppAudit(CRUDPlus[HasnAiNativeAppAudit]):
    async def get(self, db: AsyncSession, pk: int) -> HasnAiNativeAppAudit | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnAiNativeAppAudit]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAiNativeAppAuditParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAiNativeAppAuditParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_ai_native_app_audit_dao: CRUDHasnAiNativeAppAudit = CRUDHasnAiNativeAppAudit(HasnAiNativeAppAudit)
