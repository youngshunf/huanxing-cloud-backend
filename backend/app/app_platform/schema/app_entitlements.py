from datetime import datetime
from decimal import Decimal

from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AppEntitlementsSchemaBase(SchemaBase):
    """App 购买凭证基础模型"""
    entitlement_id: str | UUID = Field(description='凭证 ID')
    owner_id: str = Field(description='None')
    listing_id: str | UUID = Field(description='None')
    installation_id: str | None = Field(None, description='None')
    pricing_model: str = Field(description='定价模式 (free:免费:green/one_time:一次性:blue/subscription:订阅:orange/usage_based:按量:purple)')
    amount_paid: Decimal | None = Field(None, description='None')
    status: str = Field(description='状态 (active:活跃:green/expired:已过期:gray/cancelled:已取消:orange/refunded:已退款:red/suspended:已暂停:red)')
    purchased_at: datetime = Field(description='None')
    expires_at: datetime | None = Field(None, description='None')
    created_time: datetime = Field(description='None')
    updated_time: datetime = Field(description='None')


class CreateAppEntitlementsParam(AppEntitlementsSchemaBase):
    """创建App 购买凭证参数"""


class UpdateAppEntitlementsParam(AppEntitlementsSchemaBase):
    """更新App 购买凭证参数"""


class DeleteAppEntitlementsParam(SchemaBase):
    """删除App 购买凭证参数"""

    pks: list[int] = Field(description='App 购买凭证 ID 列表')


class GetAppEntitlementsDetail(AppEntitlementsSchemaBase):
    """App 购买凭证详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
