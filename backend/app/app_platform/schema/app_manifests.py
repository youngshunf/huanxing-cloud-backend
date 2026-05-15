from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppManifestsSchemaBase(SchemaBase):
    """App 清单基础模型"""
    app_id: str = Field(description='App ID')
    developer_id: str | UUID = Field(description='开发者 ID')
    namespace: str = Field(description='None')
    name: str = Field(description='None')
    display_name: str = Field(description='显示名称')
    description: str = Field(description='None')
    icon_url: str | None = Field(None, description='None')
    current_version: str = Field(description='None')
    backend_runtime_mode: str = Field(description='后端运行模式 (platform_hosted:平台托管:blue/external_hosted:外部托管:green)')
    frontend_hosting_mode: str = Field(description='前端托管模式 (none:无前端:gray/platform_hosted:平台托管:blue/external_hosted:外部托管:green)')
    requested_scopes: dict = Field(description='None')
    category: str | None = Field(None, description='None')
    tags: dict | None = Field(None, description='None')
    status: str = Field(description='状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/archived:已归档:gray)')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppManifestsParam(AppManifestsSchemaBase):
    """创建App 清单参数"""


class UpdateAppManifestsParam(AppManifestsSchemaBase):
    """更新App 清单参数"""


class DeleteAppManifestsParam(SchemaBase):
    """删除App 清单参数"""

    pks: list[int] = Field(description='App 清单 ID 列表')


class GetAppManifestsDetail(AppManifestsSchemaBase):
    """App 清单详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
