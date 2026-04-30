from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnSuppressedMessagesSchemaBase(SchemaBase):
    """HASN Runtime 抑制箱 / owner 可拉取消息基础模型"""
    message_id: int = Field(description='已入 inbox 的消息 ID')
    owner_id: str = Field(description='Owner hasn_id')
    hasn_id: str = Field(description='被抑制的 Agent/Human inbox 主体 hasn_id')
    conversation_id: str | UUID = Field(description='原会话 ID（不得因 Runtime 状态分裂会话）')
    suppress_reason: str = Field(description='抑制原因 (runtime_unavailable:Runtime不可用:orange/adapter_missing:Adapter缺失:red/handle_unavailable:Handle不可用:orange/owner_confirmation_required:需Owner确认:purple/policy_suppressed:策略抑制:gray)')
    dispatch_status: str = Field(description='Runtime 调度状态 (runtime_unavailable:Runtime不可用:orange/dispatch_failed:派发失败:red/suppressed_by_policy:策略抑制:purple/pending_runtime:等待Runtime:blue)')
    policy_snapshot: dict = Field(description='策略快照摘要')
    runtime_summary: dict = Field(description='Runtime 脱敏摘要；禁止 workspace/endpoint/PID/CLI args/OAuth path')
    visible_to_owner: bool = Field(description='Owner 多端是否可见')
    resolved_at: datetime | None = Field(None, description='抑制状态解除时间')


class CreateHasnSuppressedMessagesParam(HasnSuppressedMessagesSchemaBase):
    """创建HASN Runtime 抑制箱 / owner 可拉取消息参数"""


class UpdateHasnSuppressedMessagesParam(HasnSuppressedMessagesSchemaBase):
    """更新HASN Runtime 抑制箱 / owner 可拉取消息参数"""


class DeleteHasnSuppressedMessagesParam(SchemaBase):
    """删除HASN Runtime 抑制箱 / owner 可拉取消息参数"""

    pks: list[int] = Field(description='HASN Runtime 抑制箱 / owner 可拉取消息 ID 列表')


class GetHasnSuppressedMessagesDetail(HasnSuppressedMessagesSchemaBase):
    """HASN Runtime 抑制箱 / owner 可拉取消息详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
