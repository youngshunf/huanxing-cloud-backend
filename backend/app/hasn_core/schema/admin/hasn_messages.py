"""HASN 消息管理端 Schema"""
from datetime import datetime
from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnMessageSchemaBase(SchemaBase):
    """消息基础 Schema"""
    conversation_id: str = Field(description='会话ID')
    from_id: str = Field(description='发送者hasn_id')
    from_type: int = Field(description='发送者类型(1=human/2=agent/3=system)')
    content: str = Field(description='消息内容')
    content_type: int | None = Field(None, description='内容类型')
    metadata: dict | None = Field(None, description='元数据(JSON)')
    reply_to: int | None = Field(None, description='引用消息ID')
    status: int | None = Field(None, description='状态')


class CreateHasnMessageParam(HasnMessageSchemaBase):
    """创建消息参数"""


class UpdateHasnMessageParam(HasnMessageSchemaBase):
    """更新消息参数"""


class DeleteHasnMessageParam(SchemaBase):
    """删除消息参数"""
    pks: list[int] = Field(description='消息 ID 列表')


class GetHasnMessageDetail(HasnMessageSchemaBase):
    """消息详情"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
