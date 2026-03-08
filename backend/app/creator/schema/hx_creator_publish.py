from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorPublishSchemaBase(SchemaBase):
    """发布记录基础模型"""
    content_id: int = Field(description='关联内容ID')
    account_id: int | None = Field(None, description='关联平台账号ID')
    user_id: int = Field(description='关联用户ID')
    platform: str = Field(description='发布平台')
    publish_url: str | None = Field(None, description='发布链接')
    status: str | None = Field(None, description='状态：pending/published/failed/deleted')
    method: str | None = Field(None, description='发布方式：manual/auto/scheduled')
    error_message: str | None = Field(None, description='错误信息')
    published_at: datetime | None = Field(None, description='发布时间')
    views: int | None = Field(None, description='阅读量')
    likes: int | None = Field(None, description='点赞数')
    comments: int | None = Field(None, description='评论数')
    shares: int | None = Field(None, description='分享数')
    favorites: int | None = Field(None, description='收藏数')
    metrics_json: dict | None = Field(None, description='更多数据指标JSON')
    metrics_updated_at: datetime | None = Field(None, description='指标更新时间')


class CreateHxCreatorPublishParam(HxCreatorPublishSchemaBase):
    """创建发布记录参数"""


class UpdateHxCreatorPublishParam(HxCreatorPublishSchemaBase):
    """更新发布记录参数"""


class DeleteHxCreatorPublishParam(SchemaBase):
    """删除发布记录参数"""

    pks: list[int] = Field(description='发布记录 ID 列表')


class GetHxCreatorPublishDetail(HxCreatorPublishSchemaBase):
    """发布记录详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
