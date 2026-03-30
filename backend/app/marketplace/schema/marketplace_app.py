from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class MarketplaceAppSchemaBase(SchemaBase):
    """技能市场应用基础模型"""
    app_id: str = Field(description='应用唯一标识')
    name: str = Field(description='应用名称')
    description: str | None = Field(None, description='应用描述')
    icon_url: str | None = Field(None, description='应用图标URL')
    emoji: str | None = Field(None, description='emoji图标')
    author_id: int | None = Field(None, description='作者用户ID')
    author_name: str | None = Field(None, description='作者名称')
    category: str | None = Field(None, description='分类')
    tags: str | None = Field(None, description='标签，逗号分隔')
    pricing_type: str = Field(description='定价类型 (free:免费:green/paid:付费:orange/subscription:订阅:blue)')
    price: Decimal = Field(description='价格')
    is_private: bool = Field(description='是否私有')
    is_official: bool = Field(description='是否官方应用')
    download_count: int = Field(description='下载次数')
    skill_dependencies: str | None = Field(None, description='依赖的技能ID列表，逗号分隔')
    sop_dependencies: str | None = Field(None, description='依赖的SOP ID列表，逗号分隔')


class CreateMarketplaceAppParam(MarketplaceAppSchemaBase):
    """创建技能市场应用参数"""


class UpdateMarketplaceAppParam(MarketplaceAppSchemaBase):
    """更新技能市场应用参数"""


class DeleteMarketplaceAppParam(SchemaBase):
    """删除技能市场应用参数"""

    pks: list[int] = Field(description='技能市场应用 ID 列表')


class GetMarketplaceAppDetail(MarketplaceAppSchemaBase):
    """技能市场应用详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    latest_version: str | None = Field(None, description='最新版本号')
    created_time: datetime
    updated_time: datetime | None = None
