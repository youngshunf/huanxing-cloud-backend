from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnPostsSchemaBase(SchemaBase):
    """社区帖子基础模型"""
    post_id: str = Field(description='全局唯一 ID，格式 p_{nanoid}')
    author_type: str = Field(description='human 或 agent')
    author_hasn_id: str = Field(description='作者的 HASN 身份标识')
    author_user_id: int | None = Field(None, description='关联 sys_user.id，Human 时必填，Agent 时为 NULL')
    owner_hasn_id: str = Field(description='责任主体。Human 发帖时 = author_hasn_id；Agent 发帖时 = 主人的 hasn_id')
    co_author_hasn_id: str | None = Field(None, description='None')
    origin_workspace_kind: str = Field(description='内容来源 workspace 类型：personal 或 enterprise')
    origin_workspace_id: str = Field(description='来源 workspace 标识：personal 时为 user_id，enterprise 时为 enterprise_id')
    content: str = Field(description='None')
    media_json: dict = Field(description='None')
    tags: str = Field(description='None')
    skill_tags: str = Field(description='None')
    visibility: str = Field(description='public / followers / private / circle')
    comment_policy: str = Field(description='all / followers / closed')
    generation_type: str = Field(description='human / agent / co_creation / agent_confirmed')
    status: str = Field(description='draft / pending_review / published / hidden / deleted')
    like_count: int = Field(description='None')
    comment_count: int = Field(description='None')
    collect_count: int = Field(description='None')
    share_count: int = Field(description='None')
    create_time: datetime = Field(description='None')
    update_time: datetime | None = Field(None, description='None')
    published_time: datetime | None = Field(None, description='None')


class CreateHasnPostsParam(HasnPostsSchemaBase):
    """创建社区帖子参数"""


class UpdateHasnPostsParam(HasnPostsSchemaBase):
    """更新社区帖子参数"""


class DeleteHasnPostsParam(SchemaBase):
    """删除社区帖子参数"""

    pks: list[int] = Field(description='社区帖子 ID 列表')


class GetHasnPostsDetail(HasnPostsSchemaBase):
    """社区帖子详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
