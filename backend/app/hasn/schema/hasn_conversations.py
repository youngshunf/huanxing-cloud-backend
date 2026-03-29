from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnConversationsSchemaBase(SchemaBase):
    """HASN 会话基础模型"""
    type: str = Field(description='会话类型 (direct:单聊:blue/group:群聊:green)')
    relation_type: str | None = Field(None, description='关系类型 (social:社交:blue/commerce:商业:orange/service:履约:green/professional:专业:purple/platform:平台:cyan)')
    participant_a_id: str = Field(description='参与方 A hasn_id（单聊必填，群聊=创建者）')
    participant_b_id: str | None = Field(None, description='参与方 B hasn_id（单聊必填，群聊为 NULL）')
    participant_a_type: str = Field(description='参与方 A 类型 (human:人类:blue/agent:代理:green)')
    participant_b_type: str | None = Field(None, description='参与方 B 类型 (human:人类:blue/agent:代理:green)')
    trade_session_id: str | UUID | None = Field(None, description='关联交易会话 ID')
    group_id: str | None = Field(None, description='群组公开标识（格式: g:500001，type=group 时有值）')
    group_name: str | None = Field(None, description='群名称（type=group 时有值）')
    group_description: str | None = Field(None, description='群描述（type=group 时有值）')
    group_avatar_url: str | None = Field(None, description='群头像 URL（type=group 时有值）')
    group_owner_id: str | None = Field(None, description='群主 hasn_id（type=group 时有值）')
    agent_policy: str = Field(description='Agent 发言策略 (free:自由:green/mention_only:@提及:blue/silent:静默:gray/no_agent:禁止:red)')
    join_policy: str = Field(description='加入策略 (open:开放:green/invite_only:仅邀请:blue/approval:需审核:orange)')
    max_members: int = Field(description='最大成员数')
    allow_invite: bool = Field(description='成员是否可邀请')
    mute_all: bool = Field(description='全员禁言')
    member_count: int = Field(description='当前成员数')
    last_message_id: int | None = Field(None, description='最后一条消息 ID')
    last_message_at: datetime | None = Field(None, description='最后消息时间')
    last_message_preview: str | None = Field(None, description='最后消息预览')
    last_message_from: str | None = Field(None, description='最后消息发送方 hasn_id')
    message_count: int = Field(description='消息总数')
    status: str = Field(description='状态 (active:活跃:green/archived:已归档:gray/disbanded:已解散:red)')


class CreateHasnConversationsParam(HasnConversationsSchemaBase):
    """创建HASN 会话参数"""


class UpdateHasnConversationsParam(HasnConversationsSchemaBase):
    """更新HASN 会话参数"""


class DeleteHasnConversationsParam(SchemaBase):
    """删除HASN 会话参数"""

    pks: list[int] = Field(description='HASN 会话 ID 列表')


class GetHasnConversationsDetail(HasnConversationsSchemaBase):
    """HASN 会话详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
