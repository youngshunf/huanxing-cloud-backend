from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnSyncEventsSchemaBase(SchemaBase):
    """HASN 服务端下行同步事件基础模型"""
    event_id: str = Field(description='事件唯一 ID (se_{uuid})')
    owner_id: str = Field(description='事件所属 Owner hasn_id')
    hasn_id: str = Field(description='事件目标主体 hasn_id（Human 或 owned Agent）')
    event_type: str = Field(description='事件类型 (message_created:消息创建:blue/inbox_updated:Inbox更新:green/profile_updated:Profile更新:orange/runtime_warning:Runtime警告:purple/channel_bound:渠道绑定:cyan)')
    aggregate_type: str = Field(description='聚合类型 (message:消息:blue/conversation:会话:green/profile:Profile:orange/runtime:Runtime:purple/channel:渠道:cyan/sandbox:沙箱:gray)')
    aggregate_id: str = Field(description='聚合 ID')
    conversation_id: str | UUID | None = Field(None, description='关联会话 ID（如有）')
    payload: dict = Field(description='事件载荷（服务端权威摘要，不含 Runtime 私有本地态）')
    revision: int = Field(description='Owner 维度单调递增 revision')
    occurred_at: datetime = Field(description='事件发生时间')
    expires_at: datetime | None = Field(None, description='事件保留到期时间（可空）')


class CreateHasnSyncEventsParam(HasnSyncEventsSchemaBase):
    """创建HASN 服务端下行同步事件参数"""


class UpdateHasnSyncEventsParam(HasnSyncEventsSchemaBase):
    """更新HASN 服务端下行同步事件参数"""


class DeleteHasnSyncEventsParam(SchemaBase):
    """删除HASN 服务端下行同步事件参数"""

    pks: list[int] = Field(description='HASN 服务端下行同步事件 ID 列表')


class GetHasnSyncEventsDetail(HasnSyncEventsSchemaBase):
    """HASN 服务端下行同步事件详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
