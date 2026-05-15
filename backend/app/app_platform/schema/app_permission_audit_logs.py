from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppPermissionAuditLogsSchemaBase(SchemaBase):
    """权限审计日志基础模型"""
    owner_id: str = Field(description='Owner ID')
    installation_id: str = Field(description='Installation ID')
    app_id: str = Field(description='App ID')
    agent_id: str | None = Field(None, description='Agent ID')
    action: str = Field(description='操作类型')
    scope: str = Field(description='权限 Scope')
    resource_type: str | None = Field(None, description='资源类型')
    resource_id: str | None = Field(None, description='资源 ID')
    result: str = Field(description='结果')
    error_message: str | None = Field(None, description='错误信息')
    details: dict | None = Field(None, description='详细信息')
    request_id: str | None = Field(None, description='请求 ID')
    user_agent: str | None = Field(None, description='User Agent')
    ip_address: str | None = Field(None, description='IP 地址')
    created_time: datetime = Field(description='创建时间')


class CreateAppPermissionAuditLogsParam(AppPermissionAuditLogsSchemaBase):
    """创建权限审计日志参数"""


class UpdateAppPermissionAuditLogsParam(AppPermissionAuditLogsSchemaBase):
    """更新权限审计日志参数"""


class DeleteAppPermissionAuditLogsParam(SchemaBase):
    """删除权限审计日志参数"""

    pks: list[int] = Field(description='权限审计日志 ID 列表')


class GetAppPermissionAuditLogsDetail(AppPermissionAuditLogsSchemaBase):
    """权限审计日志详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
