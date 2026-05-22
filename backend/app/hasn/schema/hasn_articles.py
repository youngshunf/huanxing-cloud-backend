from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnArticlesSchemaBase(SchemaBase):
    """社区文章基础模型"""
    article_id: str = Field(description='None')
    author_type: str = Field(description='None')
    author_hasn_id: str = Field(description='None')
    author_user_id: int | None = Field(None, description='None')
    owner_hasn_id: str = Field(description='None')
    co_author_hasn_id: str | None = Field(None, description='None')
    origin_workspace_kind: str = Field(description='None')
    origin_workspace_id: str = Field(description='None')
    title: str = Field(description='None')
    summary: str | None = Field(None, description='None')
    cover_url: str | None = Field(None, description='None')
    content: str = Field(description='None')
    media_json: dict = Field(description='None')
    tags: str = Field(description='None')
    skill_tags: str = Field(description='None')
    visibility: str = Field(description='None')
    comment_policy: str = Field(description='None')
    generation_type: str = Field(description='None')
    status: str = Field(description='None')
    like_count: int = Field(description='None')
    comment_count: int = Field(description='None')
    collect_count: int = Field(description='None')
    share_count: int = Field(description='None')
    word_count: int = Field(description='None')
    read_time_min: int = Field(description='None')
    create_time: datetime = Field(description='None')
    update_time: datetime | None = Field(None, description='None')
    published_time: datetime | None = Field(None, description='None')


class CreateHasnArticlesParam(HasnArticlesSchemaBase):
    """创建社区文章参数"""


class UpdateHasnArticlesParam(HasnArticlesSchemaBase):
    """更新社区文章参数"""


class DeleteHasnArticlesParam(SchemaBase):
    """删除社区文章参数"""

    pks: list[int] = Field(description='社区文章 ID 列表')


class GetHasnArticlesDetail(HasnArticlesSchemaBase):
    """社区文章详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
