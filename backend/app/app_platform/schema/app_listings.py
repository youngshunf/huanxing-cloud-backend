from datetime import datetime
from decimal import Decimal

from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppListingsSchemaBase(SchemaBase):
    """应用市场列表基础模型"""
    listing_id: str | UUID = Field(description='Listing ID')
    app_id: str = Field(description='None')
    version_id: str | UUID = Field(description='None')
    visibility: str = Field(description='可见性 (private:私有:gray/public:公开:green)')
    title: str = Field(description='None')
    description_long: str = Field(description='None')
    pricing_model: str = Field(description='定价模式 (free:免费:green/one_time:一次性付费:blue/subscription:订阅:orange/usage_based:按量计费:purple)')
    price_amount: Decimal | None = Field(None, description='None')
    install_count: int = Field(description='None')
    rating_average: Decimal | None = Field(None, description='None')
    status: str = Field(description='状态 (draft:草稿:gray/pending_review:待审核:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/unlisted:已下架:orange)')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppListingsParam(AppListingsSchemaBase):
    """创建应用市场列表参数"""


class UpdateAppListingsParam(AppListingsSchemaBase):
    """更新应用市场列表参数"""


class DeleteAppListingsParam(SchemaBase):
    """删除应用市场列表参数"""

    pks: list[int] = Field(description='应用市场列表 ID 列表')


class GetAppListingsDetail(AppListingsSchemaBase):
    """应用市场列表详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
