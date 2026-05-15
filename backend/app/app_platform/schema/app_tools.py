from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppToolsSchemaBase(SchemaBase):
    """App Tool 定义基础模型"""
    tool_id: str = Field(description='Tool ID')
    app_id: str = Field(description='None')
    version_id: str | UUID = Field(description='None')
    tool_name: str = Field(description='None')
    display_name: str = Field(description='None')
    description: str = Field(description='None')
    input_schema: dict = Field(description='None')
    output_schema: dict = Field(description='None')
    visibility: str = Field(description='可见性 (private:私有:gray/public_service:公开服务:green)')
    risk_level: str = Field(description='风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)')
    required_scopes: dict = Field(description='None')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppToolsParam(AppToolsSchemaBase):
    """创建App Tool 定义参数"""


class UpdateAppToolsParam(AppToolsSchemaBase):
    """更新App Tool 定义参数"""


class DeleteAppToolsParam(SchemaBase):
    """删除App Tool 定义参数"""

    pks: list[int] = Field(description='App Tool 定义 ID 列表')


class GetAppToolsDetail(AppToolsSchemaBase):
    """App Tool 定义详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
