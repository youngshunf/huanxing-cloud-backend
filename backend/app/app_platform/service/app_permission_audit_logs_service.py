from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_permission_audit_logs import app_permission_audit_logs_dao
from backend.app.app_platform.model import AppPermissionAuditLogs
from backend.app.app_platform.schema.app_permission_audit_logs import CreateAppPermissionAuditLogsParam, DeleteAppPermissionAuditLogsParam, UpdateAppPermissionAuditLogsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppPermissionAuditLogsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppPermissionAuditLogs:
        """
        获取权限审计日志

        :param db: 数据库会话
        :param pk: 权限审计日志 ID
        :return:
        """
        app_permission_audit_logs = await app_permission_audit_logs_dao.get(db, pk)
        if not app_permission_audit_logs:
            raise errors.NotFoundError(msg='权限审计日志不存在')
        return app_permission_audit_logs

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取权限审计日志列表

        :param db: 数据库会话
        :return:
        """
        app_permission_audit_logs_select = await app_permission_audit_logs_dao.get_select()
        return await paging_data(db, app_permission_audit_logs_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppPermissionAuditLogs]:
        """
        获取所有权限审计日志

        :param db: 数据库会话
        :return:
        """
        app_permission_audit_logss = await app_permission_audit_logs_dao.get_all(db)
        return app_permission_audit_logss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppPermissionAuditLogsParam) -> None:
        """
        创建权限审计日志

        :param db: 数据库会话
        :param obj: 创建权限审计日志参数
        :return:
        """
        await app_permission_audit_logs_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppPermissionAuditLogsParam) -> int:
        """
        更新权限审计日志

        :param db: 数据库会话
        :param pk: 权限审计日志 ID
        :param obj: 更新权限审计日志参数
        :return:
        """
        count = await app_permission_audit_logs_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppPermissionAuditLogsParam) -> int:
        """
        删除权限审计日志

        :param db: 数据库会话
        :param obj: 权限审计日志 ID 列表
        :return:
        """
        count = await app_permission_audit_logs_dao.delete(db, obj.pks)
        return count


app_permission_audit_logs_service: AppPermissionAuditLogsService = AppPermissionAuditLogsService()
