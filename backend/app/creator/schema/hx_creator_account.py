from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorAccountSchemaBase(SchemaBase):
    """平台账号基础模型"""
    project_id: int = Field(description='关联项目ID')
    user_id: int = Field(description='关联用户ID')
    platform: str = Field(description='平台标识：xiaohongshu/douyin/wechat/weibo/bilibili')
    platform_uid: str | None = Field(None, description='平台用户ID')
    nickname: str | None = Field(None, description='平台昵称')
    avatar_url: str | None = Field(None, description='头像URL')
    bio: str | None = Field(None, description='平台简介')
    home_url: str | None = Field(None, description='主页链接')
    followers: int | None = Field(None, description='粉丝数')
    following: int | None = Field(None, description='关注数')
    total_likes: int | None = Field(None, description='总点赞数')
    total_favorites: int | None = Field(None, description='总收藏数')
    total_comments: int | None = Field(None, description='总评论数')
    total_posts: int | None = Field(None, description='总发布数')
    metrics_json: dict | None = Field(None, description='更多指标JSON')
    metrics_updated_at: datetime | None = Field(None, description='指标更新时间')
    auth_status: str | None = Field(None, description='登录状态：not_configured/active/expired')
    is_primary: bool | None = Field(None, description='是否主账号')
    notes: str | None = Field(None, description='备注')


class CreateHxCreatorAccountParam(HxCreatorAccountSchemaBase):
    """创建平台账号参数"""


class UpdateHxCreatorAccountParam(HxCreatorAccountSchemaBase):
    """更新平台账号参数"""


class DeleteHxCreatorAccountParam(SchemaBase):
    """删除平台账号参数"""

    pks: list[int] = Field(description='平台账号 ID 列表')


class GetHxCreatorAccountDetail(HxCreatorAccountSchemaBase):
    """平台账号详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
