"""HASN 审计日志管理端 Service"""
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.admin.hasn_audit_log import hasn_audit_log_admin_dao
from backend.app.hasn_core.model import HasnAuditLog
from backend.app.hasn_core.schema.admin.hasn_audit_log import CreateHasnAuditLogParam, DeleteHasnAuditLogParam, UpdateHasnAuditLogParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnAuditLogAdminService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnAuditLog:
        obj = await hasn_audit_log_admin_dao.get(db, pk)
        if not obj:
            raise errors.NotFoundError(msg='审计日志不存在')
        return obj

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await hasn_audit_log_admin_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnAuditLogParam) -> None:
        await hasn_audit_log_admin_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnAuditLogParam) -> int:
        return await hasn_audit_log_admin_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnAuditLogParam) -> int:
        return await hasn_audit_log_admin_dao.delete(db, obj.pks)


hasn_audit_log_admin_service: HasnAuditLogAdminService = HasnAuditLogAdminService()
