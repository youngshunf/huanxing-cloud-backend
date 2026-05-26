from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class MarketplaceDownloadHistorySchemaBase(SchemaBase):
    """技能市场下载历史基础模型"""
    skill_id: str = Field(description='技能ID')
    version: str = Field(description='版本号')
    user_id: int | None = Field(None, description='用户ID')
    ip_address: str | None = Field(None, description='IP地址')
    user_agent: str | None = Field(None, description='用户代理')
    downloaded_at: datetime | None = Field(None, description='下载时间')


class CreateMarketplaceDownloadHistoryParam(MarketplaceDownloadHistorySchemaBase):
    """创建技能市场下载历史参数"""


class UpdateMarketplaceDownloadHistoryParam(MarketplaceDownloadHistorySchemaBase):
    """更新技能市场下载历史参数"""


class DeleteMarketplaceDownloadHistoryParam(SchemaBase):
    """删除技能市场下载历史参数"""

    pks: list[int] = Field(description='技能市场下载历史 ID 列表')


class GetMarketplaceDownloadHistoryDetail(MarketplaceDownloadHistorySchemaBase):
    """技能市场下载历史详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
