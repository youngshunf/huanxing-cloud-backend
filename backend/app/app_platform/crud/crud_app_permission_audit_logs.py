from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppPermissionAuditLogs
from backend.app.app_platform.schema.app_permission_audit_logs import CreateAppPermissionAuditLogsParam, UpdateAppPermissionAuditLogsParam


class CRUDAppPermissionAuditLogs(CRUDPlus[AppPermissionAuditLogs]):
    async def get(self, db: AsyncSession, pk: int) -> AppPermissionAuditLogs | None:
        """
        获取权限审计日志

        :param db: 数据库会话
        :param pk: 权限审计日志 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取权限审计日志列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppPermissionAuditLogs]:
        """
        获取所有权限审计日志

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppPermissionAuditLogsParam) -> None:
        """
        创建权限审计日志

        :param db: 数据库会话
        :param obj: 创建权限审计日志参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppPermissionAuditLogsParam) -> int:
        """
        更新权限审计日志

        :param db: 数据库会话
        :param pk: 权限审计日志 ID
        :param obj: 更新 权限审计日志参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除权限审计日志

        :param db: 数据库会话
        :param pks: 权限审计日志 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_installation(
        self,
        db: AsyncSession,
        installation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AppPermissionAuditLogs]:
        """
        根据 installation_id 获取审计日志

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param limit: 限制数量
        :param offset: 偏移量
        :return:
        """
        # TODO: 实现分页查询
        return await self.select_models_by_column(db, installation_id=installation_id)

    async def get_by_action(
        self,
        db: AsyncSession,
        installation_id: str,
        action: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[AppPermissionAuditLogs]:
        """
        根据 action 获取审计日志

        :param db: 数据库会话
        :param installation_id: Installation ID
        :param action: 操作类型
        :param limit: 限制数量
        :param offset: 偏移量
        :return:
        """
        # TODO: 实现分页查询
        return await self.select_models_by_column(
            db,
            installation_id=installation_id,
            action=action,
        )


app_permission_audit_logs_dao: CRUDAppPermissionAuditLogs = CRUDAppPermissionAuditLogs(AppPermissionAuditLogs)
