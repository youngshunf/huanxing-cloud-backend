"""HASN 会话管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnConversationSchemaBase(SchemaBase):
    """会话基础 Schema"""
    type: str = Field(description='类型(direct/group)')
    participant_a: str | None = Field(None, description='参与者A')
    participant_b: str | None = Field(None, description='参与者B')
    name: str | None = Field(None, description='会话名称')
    group_star_id: str | None = Field(None, description='群唤星号')
    group_avatar: str | None = Field(None, description='群头像')
    group_description: str | None = Field(None, description='群描述')
    agent_policy: str | None = Field(None, description='Agent发言策略')
    max_members: int | None = Field(None, description='最大成员数')
    creator_id: str | None = Field(None, description='创建者hasn_id')
    message_count: int | None = Field(None, description='消息数')
    status: str | None = Field(None, description='状态')


class CreateHasnConversationParam(HasnConversationSchemaBase):
    """创建会话参数"""


class UpdateHasnConversationParam(HasnConversationSchemaBase):
    """更新会话参数"""


class DeleteHasnConversationParam(SchemaBase):
    """删除会话参数"""
    pks: list[str] = Field(description='会话 ID 列表')


class GetHasnConversationDetail(HasnConversationSchemaBase):
    """会话详情"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_time: datetime
    updated_time: datetime | None = None
