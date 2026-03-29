from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnConversationsSchemaBase(SchemaBase):
    """HASN 会话基础模型"""
    type: str = Field(default='direct', description='会话类型: direct/group')
    relation_type: str | None = Field(default='social', description='关系类型: social/commerce/service/professional/platform')
    participant_a_id: str = Field(description='参与方 A 的 hasn_id')
    participant_b_id: str | None = Field(None, description='参与方 B 的 hasn_id (群聊为 NULL)')
    participant_a_type: str = Field(default='human', description='参与方 A 类型: human/agent')
    participant_b_type: str | None = Field(default='human', description='参与方 B 类型: human/agent')
    trade_session_id: str | None = Field(None, description='关联交易会话 ID')


class CreateHasnConversationsParam(HasnConversationsSchemaBase):
    """创建 HASN 会话参数"""


class UpdateHasnConversationsParam(SchemaBase):
    """更新 HASN 会话参数"""
    last_message_id: int | None = Field(None, description='最后一条消息 ID')
    last_message_at: datetime | None = Field(None, description='最后消息时间')
    last_message_preview: str | None = Field(None, description='最后消息预览')
    last_message_from: str | None = Field(None, description='最后消息发送方 hasn_id')
    message_count: int | None = Field(None, description='消息总数')


class DeleteHasnConversationsParam(SchemaBase):
    """删除 HASN 会话参数"""
    pks: list[str] = Field(description='HASN 会话 ID 列表 (UUID)')


class GetHasnConversationsDetail(HasnConversationsSchemaBase):
    """HASN 会话详情"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    last_message_id: int | None = None
    last_message_at: datetime | None = None
    last_message_preview: str | None = None
    last_message_from: str | None = None
    message_count: int = 0
    created_time: datetime
    updated_time: datetime | None = None
