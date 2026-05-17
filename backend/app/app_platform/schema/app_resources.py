from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppResourcesSchemaBase(SchemaBase):
    """App Resource 定义基础模型"""
    resource_id: str = Field(description='Resource ID')
    app_id: str = Field(description='None')
    version_id: str | UUID = Field(description='None')
    resource_name: str = Field(description='None')
    display_name: str = Field(description='None')
    description: str = Field(description='None')
    schema_json_: dict = Field(alias='schema_json', description='None')
    storage_strategy: str = Field(description='存储策略 (jsonb:JSONB存储:blue/dedicated_table:独立表:green)')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppResourcesParam(AppResourcesSchemaBase):
    """创建App Resource 定义参数"""


class UpdateAppResourcesParam(AppResourcesSchemaBase):
    """更新App Resource 定义参数"""


class DeleteAppResourcesParam(SchemaBase):
    """删除App Resource 定义参数"""

    pks: list[int] = Field(description='App Resource 定义 ID 列表')


class GetAppResourcesDetail(AppResourcesSchemaBase):
    """App Resource 定义详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
