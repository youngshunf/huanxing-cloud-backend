from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppDynamicPermissionRequestsSchemaBase(SchemaBase):
    """动态权限请求基础模型"""
    request_id: str | UUID = Field(description='请求 ID')
    installation_id: str = Field(description='关联的 Installation ID')
    scope: str = Field(description='请求的权限标识')
    requested_at: datetime = Field(description='请求时间')
    request_reason: str = Field(description='App 说明为什么需要这个权限')
    request_context: dict | None = Field(None, description='请求时的上下文信息（JSONB）')
    status: str = Field(description='状态 (pending:待处理:blue/approved:已批准:green/denied:已拒绝:red/expired:已过期:gray)')
    decided_at: datetime | None = Field(None, description='决策时间')
    decided_by: str | None = Field(None, description='决策者 Owner ID')
    decision_reason: str | None = Field(None, description='决策理由')
    expires_at: datetime = Field(description='请求过期时间（默认 24 小时）')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime = Field(description='更新时间')


class CreateAppDynamicPermissionRequestsParam(AppDynamicPermissionRequestsSchemaBase):
    """创建动态权限请求参数"""


class UpdateAppDynamicPermissionRequestsParam(AppDynamicPermissionRequestsSchemaBase):
    """更新动态权限请求参数"""


class DeleteAppDynamicPermissionRequestsParam(SchemaBase):
    """删除动态权限请求参数"""

    pks: list[int] = Field(description='动态权限请求 ID 列表')


class GetAppDynamicPermissionRequestsDetail(AppDynamicPermissionRequestsSchemaBase):
    """动态权限请求详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
