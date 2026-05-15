#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Audit Client

应用审计能力客户端
"""
from typing import Optional, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.sdk.app_context import AppContext
from backend.app.app_platform.crud.crud_app_permission_audit_logs import CRUDAppPermissionAuditLogs
from backend.app.app_platform.schema.app_permission_audit_logs import CreateAppPermissionAuditLogsParam
from backend.common.log import log


class AppAuditClient:
    """
    应用审计客户端

    提供审计日志记录能力
    """

    def __init__(self, context: AppContext, db: AsyncSession):
        """
        初始化审计客户端

        :param context: 应用上下文
        :param db: 数据库会话
        """
        self.context = context
        self.db = db
        self.crud = CRUDAppPermissionAuditLogs()

    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        result: str = 'success',
    ) -> None:
        """
        记录操作日志

        :param action: 操作类型（如 'tool.call', 'data.read', 'data.write'）
        :param resource_type: 资源类型（如 'tool', 'resource', 'event'）
        :param resource_id: 资源 ID
        :param details: 详细信息
        :param result: 结果（'success', 'failure', 'denied'）
        """
        await self.crud.create(
            db=self.db,
            obj=CreateAppPermissionAuditLogsParam(
                owner_id=self.context.owner_id,
                installation_id=self.context.installation_id,
                app_id=self.context.app_id,
                agent_id=self.context.agent_id,
                action=action,
                scope=f"hasn.app.{action}",
                resource_type=resource_type,
                resource_id=resource_id,
                result=result,
                details=details,
                request_id=self.context.request_id,
                user_agent=self.context.user_agent,
                ip_address=self.context.ip_address,
            ),
        )

    async def log_tool_call(
        self,
        tool_id: str,
        tool_name: str,
        parameters: dict[str, Any],
        result: str = 'success',
        error: Optional[str] = None,
    ) -> None:
        """
        记录 Tool 调用日志

        :param tool_id: Tool ID
        :param tool_name: Tool 名称
        :param parameters: 调用参数
        :param result: 结果
        :param error: 错误信息
        """
        await self.log_action(
            action='tool.call',
            resource_type='tool',
            resource_id=tool_id,
            details={
                'tool_name': tool_name,
                'parameters': parameters,
                'error': error,
            },
            result=result,
        )

    async def log_data_access(
        self,
        operation: str,
        resource_id: str,
        record_key: str,
        result: str = 'success',
    ) -> None:
        """
        记录数据访问日志

        :param operation: 操作类型（'read', 'write', 'delete'）
        :param resource_id: Resource ID
        :param record_key: 记录键
        :param result: 结果
        """
        await self.log_action(
            action=f'data.{operation}',
            resource_type='resource',
            resource_id=resource_id,
            details={
                'record_key': record_key,
            },
            result=result,
        )

    async def get_logs(
        self,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        获取审计日志

        :param action: 操作类型过滤
        :param resource_type: 资源类型过滤
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param limit: 限制数量
        :param offset: 偏移量
        :return: 审计日志列表
        """
        if action:
            logs = await self.crud.get_by_action(
                db=self.db,
                installation_id=self.context.installation_id,
                action=action,
                limit=limit,
                offset=offset,
            )
        else:
            logs = await self.crud.get_by_installation(
                db=self.db,
                installation_id=self.context.installation_id,
                limit=limit,
                offset=offset,
            )

        return [
            {
                'id': str(log.id),
                'action': log.action,
                'scope': log.scope,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'result': log.result,
                'error_message': log.error_message,
                'details': log.details,
                'created_at': log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]
