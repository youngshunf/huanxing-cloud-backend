from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_audit_log import hasn_audit_log_dao
from backend.app.hasn.model import HasnAuditLog
from backend.app.hasn.schema.hasn_audit_log import CreateHasnAuditLogParam, DeleteHasnAuditLogParam, UpdateHasnAuditLogParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnAuditLogService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnAuditLog:
        """
        获取HASN 审计日志

        :param db: 数据库会话
        :param pk: HASN 审计日志 ID
        :return:
        """
        hasn_audit_log = await hasn_audit_log_dao.get(db, pk)
        if not hasn_audit_log:
            raise errors.NotFoundError(msg='HASN 审计日志不存在')
        return hasn_audit_log

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN 审计日志列表

        :param db: 数据库会话
        :return:
        """
        hasn_audit_log_select = await hasn_audit_log_dao.get_select()
        return await paging_data(db, hasn_audit_log_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnAuditLog]:
        """
        获取所有HASN 审计日志

        :param db: 数据库会话
        :return:
        """
        hasn_audit_logs = await hasn_audit_log_dao.get_all(db)
        return hasn_audit_logs

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnAuditLogParam) -> None:
        """
        创建HASN 审计日志

        :param db: 数据库会话
        :param obj: 创建HASN 审计日志参数
        :return:
        """
        await hasn_audit_log_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnAuditLogParam) -> int:
        """
        更新HASN 审计日志

        :param db: 数据库会话
        :param pk: HASN 审计日志 ID
        :param obj: 更新HASN 审计日志参数
        :return:
        """
        count = await hasn_audit_log_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnAuditLogParam) -> int:
        """
        删除HASN 审计日志

        :param db: 数据库会话
        :param obj: HASN 审计日志 ID 列表
        :return:
        """
        count = await hasn_audit_log_dao.delete(db, obj.pks)
        return count


hasn_audit_log_service: HasnAuditLogService = HasnAuditLogService()
