from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorProjectSchemaBase(SchemaBase):
    """创作项目基础模型"""
    user_id: int = Field(description='关联用户ID')
    name: str = Field(description='项目名称（如：小红书美食号）')
    description: str | None = Field(None, description='项目描述')
    platform: str = Field(description='主平台：xiaohongshu/douyin/wechat/weibo/bilibili')
    platforms: dict | None = Field(None, description='多平台JSON数组')
    avatar_url: str | None = Field(None, description='项目头像URL')
    is_active: bool | None = Field(None, description='是否为当前活跃项目')


class CreateHxCreatorProjectParam(HxCreatorProjectSchemaBase):
    """创建创作项目参数"""


class UpdateHxCreatorProjectParam(HxCreatorProjectSchemaBase):
    """更新创作项目参数"""


class DeleteHxCreatorProjectParam(SchemaBase):
    """删除创作项目参数"""

    pks: list[int] = Field(description='创作项目 ID 列表')


class GetHxCreatorProjectDetail(HxCreatorProjectSchemaBase):
    """创作项目详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
