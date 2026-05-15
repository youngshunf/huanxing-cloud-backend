from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppInstallationsSchemaBase(SchemaBase):
    """App 安装记录基础模型"""
    installation_id: str = Field(description='Installation ID')
    owner_id: str = Field(description='Owner ID')
    app_id: str = Field(description='None')
    listing_id: str | UUID = Field(description='None')
    installed_version: str = Field(description='None')
    granted_scopes: dict = Field(description='授予的权限列表（JSONB）')
    status: str = Field(description='状态 (active:活跃:green/update_available:有更新:blue/pending_reauth:待重新授权:orange/suspended:已暂停:red/revoked:已撤销:red)')
    installed_at: datetime = Field(description='None')
    last_used_at: datetime | None = Field(None, description='None')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppInstallationsParam(AppInstallationsSchemaBase):
    """创建App 安装记录参数"""


class UpdateAppInstallationsParam(AppInstallationsSchemaBase):
    """更新App 安装记录参数"""


class DeleteAppInstallationsParam(SchemaBase):
    """删除App 安装记录参数"""

    pks: list[int] = Field(description='App 安装记录 ID 列表')


class GetAppInstallationsDetail(AppInstallationsSchemaBase):
    """App 安装记录详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
