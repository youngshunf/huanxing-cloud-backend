from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class IntegrationAppsSchemaBase(SchemaBase):
    """第三方应用集成配置基础模型"""
    app_id: str = Field(description='应用唯一标识（如 clawhub）')
    app_name: str = Field(description='应用名称（如 ClawHub 技能市场）')
    app_type: str = Field(description='应用类型（用于实例化对应的集成类，如 clawhub/github/feishu）')
    base_url: str = Field(description='应用基础 URL')
    config: dict | None = Field(None, description='应用配置（JSON 格式，包含 API 端点、超时设置等）')
    is_enabled: bool = Field(description='是否启用')
    description: str | None = Field(None, description='应用描述')
    icon_url: str | None = Field(None, description='应用图标 URL')


class CreateIntegrationAppsParam(IntegrationAppsSchemaBase):
    """创建第三方应用集成配置参数"""


class UpdateIntegrationAppsParam(IntegrationAppsSchemaBase):
    """更新第三方应用集成配置参数"""


class DeleteIntegrationAppsParam(SchemaBase):
    """删除第三方应用集成配置参数"""

    pks: list[int] = Field(description='第三方应用集成配置 ID 列表')


class GetIntegrationAppsDetail(IntegrationAppsSchemaBase):
    """第三方应用集成配置详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
