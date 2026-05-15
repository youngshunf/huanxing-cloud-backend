from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppVersionsSchemaBase(SchemaBase):
    """App 版本基础模型"""
    version_id: str | UUID = Field(description='版本 ID')
    app_id: str = Field(description='App ID')
    version: str = Field(description='版本号')
    changelog: str | None = Field(None, description='None')
    manifest_snapshot: dict = Field(description='Manifest 快照（JSONB）')
    status: str = Field(description='状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/deprecated:已废弃:orange)')
    published_at: datetime | None = Field(None, description='None')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppVersionsParam(AppVersionsSchemaBase):
    """创建App 版本参数"""


class UpdateAppVersionsParam(AppVersionsSchemaBase):
    """更新App 版本参数"""


class DeleteAppVersionsParam(SchemaBase):
    """删除App 版本参数"""

    pks: list[int] = Field(description='App 版本 ID 列表')


class GetAppVersionsDetail(AppVersionsSchemaBase):
    """App 版本详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
