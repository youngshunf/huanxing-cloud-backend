from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppDataRecordsSchemaBase(SchemaBase):
    """应用数据记录表（JSONB 存储）基础模型"""
    owner_id: str = Field(description='Owner ID')
    app_id: str = Field(description='App ID')
    installation_id: str = Field(description='Installation ID')
    install_target_type: str | None = Field(None, description='安装目标类型')
    install_target_id: str | None = Field(None, description='安装目标 ID')
    resource_id: str = Field(description='Resource ID')
    record_key: str = Field(description='记录键')
    data_json: dict = Field(description='数据 JSON')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime = Field(description='更新时间')
    created_by: str | None = Field(None, description='创建者 ID')
    updated_by: str | None = Field(None, description='更新者 ID')
    version: int = Field(description='版本号')


class CreateAppDataRecordsParam(SchemaBase):
    """创建应用数据记录表（JSONB 存储）参数"""

    owner_id: str = Field(description='Owner ID')
    app_id: str = Field(description='App ID')
    installation_id: str = Field(description='Installation ID')
    resource_id: str = Field(description='Resource ID')
    record_key: str = Field(description='记录键')
    data_json: dict = Field(description='数据 JSON')
    install_target_type: str | None = Field(None, description='安装目标类型')
    install_target_id: str | None = Field(None, description='安装目标 ID')
    created_by: str | None = Field(None, description='创建者 ID')
    updated_by: str | None = Field(None, description='更新者 ID')
    version: int = Field(default=1, description='版本号')


class UpdateAppDataRecordsParam(AppDataRecordsSchemaBase):
    """更新应用数据记录表（JSONB 存储）参数"""


class DeleteAppDataRecordsParam(SchemaBase):
    """删除应用数据记录表（JSONB 存储）参数"""

    pks: list[int] = Field(description='应用数据记录表（JSONB 存储） ID 列表')


class GetAppDataRecordsDetail(AppDataRecordsSchemaBase):
    """应用数据记录表（JSONB 存储）详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
