from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HxCreatorCompetitorSchemaBase(SchemaBase):
    """竞品账号基础模型"""
    project_id: int = Field(description='关联项目ID')
    user_id: int = Field(description='关联用户ID')
    name: str = Field(description='竞品名称')
    platform: str = Field(description='平台')
    url: str | None = Field(None, description='主页链接')
    follower_count: int | None = Field(None, description='粉丝数')
    avg_likes: int | None = Field(None, description='平均点赞')
    content_style: str | None = Field(None, description='内容风格')
    strengths: str | None = Field(None, description='优势')
    notes: str | None = Field(None, description='备注')
    tags: dict | None = Field(None, description='标签JSON数组')
    last_analyzed: datetime | None = Field(None, description='最后分析时间')


class CreateHxCreatorCompetitorParam(HxCreatorCompetitorSchemaBase):
    """创建竞品账号参数"""


class UpdateHxCreatorCompetitorParam(HxCreatorCompetitorSchemaBase):
    """更新竞品账号参数"""


class DeleteHxCreatorCompetitorParam(SchemaBase):
    """删除竞品账号参数"""

    pks: list[int] = Field(description='竞品账号 ID 列表')


class GetHxCreatorCompetitorDetail(HxCreatorCompetitorSchemaBase):
    """竞品账号详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
