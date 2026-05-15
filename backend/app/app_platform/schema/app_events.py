from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppEventsSchemaBase(SchemaBase):
    """App Event 定义基础模型"""
    event_id: str = Field(description='Event ID')
    app_id: str = Field(description='None')
    version_id: str | UUID = Field(description='None')
    event_type: str = Field(description='None')
    display_name: str = Field(description='None')
    description: str = Field(description='None')
    payload_schema: dict = Field(description='None')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppEventsParam(AppEventsSchemaBase):
    """创建App Event 定义参数"""


class UpdateAppEventsParam(AppEventsSchemaBase):
    """更新App Event 定义参数"""


class DeleteAppEventsParam(SchemaBase):
    """删除App Event 定义参数"""

    pks: list[int] = Field(description='App Event 定义 ID 列表')


class GetAppEventsDetail(AppEventsSchemaBase):
    """App Event 定义详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
