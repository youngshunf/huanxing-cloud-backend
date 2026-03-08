"""HASN 审计日志管理端 CRUD"""
from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn_core.model import HasnAuditLog
from backend.app.hasn_core.schema.admin.hasn_audit_log import CreateHasnAuditLogParam, UpdateHasnAuditLogParam


class CRUDHasnAuditLogAdmin(CRUDPlus[HasnAuditLog]):
    async def get(self, db: AsyncSession, pk: int) -> HasnAuditLog | None:
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnAuditLog]:
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnAuditLogParam) -> None:
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnAuditLogParam) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_audit_log_admin_dao: CRUDHasnAuditLogAdmin = CRUDHasnAuditLogAdmin(HasnAuditLog)
