from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnUnreadCountsSchemaBase(SchemaBase):
    """HASN 未读计数基础模型"""
    hasn_id: str = Field(description='用户/Agent 的 hasn_id')
    conversation_id: str | UUID = Field(description='会话 ID')
    unread_count: int = Field(description='未读消息数')
    last_read_msg_id: int = Field(description='最后已读消息 ID')


class CreateHasnUnreadCountsParam(HasnUnreadCountsSchemaBase):
    """创建HASN 未读计数参数"""


class UpdateHasnUnreadCountsParam(HasnUnreadCountsSchemaBase):
    """更新HASN 未读计数参数"""


class DeleteHasnUnreadCountsParam(SchemaBase):
    """删除HASN 未读计数参数"""

    pks: list[int] = Field(description='HASN 未读计数 ID 列表')


class GetHasnUnreadCountsDetail(HasnUnreadCountsSchemaBase):
    """HASN 未读计数详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
