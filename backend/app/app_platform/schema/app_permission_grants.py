from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppPermissionGrantsSchemaBase(SchemaBase):
    """权限授予记录基础模型"""
    grant_id: str | UUID = Field(description='授权记录 ID')
    installation_id: str = Field(description='关联的 Installation ID')
    scope: str = Field(description='授予的权限标识')
    granted_by: str = Field(description='授予者 Owner ID')
    granted_at: datetime = Field(description='授予时间')
    grant_source: str = Field(description='授予来源 (installation:安装时:blue/dynamic_request:动态请求:green/version_upgrade:版本升级:orange)')
    status: str = Field(description='状态 (active:生效:green/revoked:已撤销:red)')
    revoked_at: datetime | None = Field(None, description='撤销时间')
    revoked_by: str | None = Field(None, description='撤销者（owner 或 platform）')
    revocation_reason: str | None = Field(None, description='撤销原因')
    last_used_at: datetime | None = Field(None, description='最后使用时间')
    usage_count: int = Field(description='使用次数')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime = Field(description='更新时间')


class CreateAppPermissionGrantsParam(SchemaBase):
    """创建权限授予记录参数"""

    installation_id: str = Field(description='关联的 Installation ID')
    scope: str = Field(description='授予的权限标识')
    granted_by: str = Field(description='授予者 Owner ID')
    grant_source: str = Field(description='授予来源 (installation:安装时:blue/dynamic_request:动态请求:green/version_upgrade:版本升级:orange)')
    status: str = Field(default='active', description='状态 (active:生效:green/revoked:已撤销:red)')
    # grant_id 和 granted_at 由数据库自动生成
    revoked_at: datetime | None = Field(None, description='撤销时间')
    revoked_by: str | None = Field(None, description='撤销者（owner 或 platform）')
    revocation_reason: str | None = Field(None, description='撤销原因')
    last_used_at: datetime | None = Field(None, description='最后使用时间')
    usage_count: int = Field(default=0, description='使用次数')


class UpdateAppPermissionGrantsParam(AppPermissionGrantsSchemaBase):
    """更新权限授予记录参数"""


class DeleteAppPermissionGrantsParam(SchemaBase):
    """删除权限授予记录参数"""

    pks: list[int] = Field(description='权限授予记录 ID 列表')


class GetAppPermissionGrantsDetail(AppPermissionGrantsSchemaBase):
    """权限授予记录详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
