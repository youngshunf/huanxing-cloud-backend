from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnCommentsSchemaBase(SchemaBase):
    """社区评论基础模型"""
    comment_id: str = Field(description='None')
    target_type: str = Field(description='post 或 article')
    target_id: str = Field(description='帖子的 post_id 或文章的 article_id')
    parent_id: str | None = Field(None, description='父评论 comment_id（楼中楼回复）')
    root_id: str | None = Field(None, description='根评论 comment_id（方便查询整个评论线程）')
    author_type: str = Field(description='None')
    author_hasn_id: str = Field(description='None')
    author_user_id: int | None = Field(None, description='None')
    owner_hasn_id: str = Field(description='None')
    origin_workspace_kind: str = Field(description='None')
    origin_workspace_id: str = Field(description='None')
    content: str = Field(description='None')
    is_auto_reply: bool = Field(description='Agent 自动回复标识，前端据此展示"自动回复"标签')
    like_count: int = Field(description='None')
    status: str = Field(description='visible / hidden / deleted')
    created_time: datetime = Field(description='None')


class CreateHasnCommentsParam(HasnCommentsSchemaBase):
    """创建社区评论参数"""


class UpdateHasnCommentsParam(HasnCommentsSchemaBase):
    """更新社区评论参数"""


class DeleteHasnCommentsParam(SchemaBase):
    """删除社区评论参数"""

    pks: list[int] = Field(description='社区评论 ID 列表')


class GetHasnCommentsDetail(HasnCommentsSchemaBase):
    """社区评论详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
