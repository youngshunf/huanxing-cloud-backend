from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class MarketplaceSopSchemaBase(SchemaBase):
    """SOP 工作流基础模型"""
    sop_id: str = Field(description='SOP唯一标识')
    name: str = Field(description='SOP名称')
    description: str | None = Field(None, description='SOP描述')
    icon_url: str | None = Field(None, description='SVG图标URL')
    emoji: str | None = Field(None, description='emoji图标')
    author_id: int | None = Field(None, description='作者用户ID')
    author_name: str | None = Field(None, description='作者名称')
    category: str | None = Field(None, description='分类')
    tags: str | None = Field(None, description='标签，逗号分隔')
    execution_mode: str | None = Field('supervised', description='执行模式')
    skill_dependencies: str | None = Field(None, description='依赖的技能ID列表，逗号分隔')
    pricing_type: str = Field(description='定价类型 (free:免费:green/paid:付费:orange)')
    price: Decimal = Field(description='价格')
    is_private: bool = Field(description='是否私有')
    is_official: bool = Field(description='是否官方SOP')
    download_count: int = Field(description='下载次数')


class CreateMarketplaceSopParam(MarketplaceSopSchemaBase):
    """创建SOP参数"""


class UpdateMarketplaceSopParam(MarketplaceSopSchemaBase):
    """更新SOP参数"""


class DeleteMarketplaceSopParam(SchemaBase):
    """删除SOP参数"""

    pks: list[int] = Field(description='SOP ID 列表')


class GetMarketplaceSopDetail(MarketplaceSopSchemaBase):
    """SOP详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    latest_version: str | None = Field(None, description='最新版本号')
    created_time: datetime
    updated_time: datetime | None = None
