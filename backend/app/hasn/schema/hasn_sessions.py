from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnSessionsSchemaBase(SchemaBase):
    """HASN 会话分层基础模型"""
    conversation_id: UUID | None = Field(None, description='关联的 conversation ID')
    session_kind: str = Field(default='conversation', description='会话类型 (conversation/task/temporary/external/system)')
    session_scope: str = Field(default='conversation_visible', description='同步范围 (conversation_visible/summary_only/local_only)')
    session_status: str = Field(default='active', description='会话状态 (active/paused/completed/archived)')
    origin_type: str | None = Field(None, description='来源类型 (ui/scheduler/external_app/api/system)')
    origin_ref: str | None = Field(None, description='来源引用 (task_id/app_id/trace_id)')
    parent_session_id: str | None = Field(None, description='父会话 ID (用于分叉)')
    fork_point_message_id: int | None = Field(None, description='分叉点消息 ID')
    summary_checkpoint_json: str | None = Field(None, description='会话摘要检查点 (JSON)')
    last_message_id: int | None = Field(None, description='最后一条消息 ID')
    last_message_at: datetime | None = Field(None, description='最后消息时间')
    message_count: int = Field(default=0, description='消息总数')


class CreateHasnSessionsParam(HasnSessionsSchemaBase):
    """创建 HASN 会话参数"""
    id: str = Field(description='会话 ID (ULID 格式)')


class UpdateHasnSessionsParam(SchemaBase):
    """更新 HASN 会话参数"""
    session_status: str | None = Field(None, description='会话状态')
    summary_checkpoint_json: str | None = Field(None, description='会话摘要检查点')
    last_message_id: int | None = Field(None, description='最后一条消息 ID')
    last_message_at: datetime | None = Field(None, description='最后消息时间')
    message_count: int | None = Field(None, description='消息总数')


class GetHasnSessionsDetail(HasnSessionsSchemaBase):
    """HASN 会话详情"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_time: datetime
    updated_time: datetime | None = None


class HasnSessionEventsSchemaBase(SchemaBase):
    """HASN 会话事件基础模型"""
    session_id: str = Field(description='会话 ID')
    event_type: str = Field(description='事件类型 (session.created/session.paused/task.started/tool.called)')
    event_seq: int = Field(default=0, description='会话内事件序号')
    payload_json: str | None = Field(None, description='事件载荷 (JSON)')
    occurred_at: datetime | None = Field(None, description='事件发生时间')


class CreateHasnSessionEventsParam(HasnSessionEventsSchemaBase):
    """创建 HASN 会话事件参数"""
    pass


class GetHasnSessionEventsDetail(HasnSessionEventsSchemaBase):
    """HASN 会话事件详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime


class HasnSessionArtifactsSchemaBase(SchemaBase):
    """HASN 会话产物基础模型"""
    session_id: str = Field(description='会话 ID')
    artifact_kind: str = Field(description='产物类型 (file/code/report/data)')
    artifact_name: str | None = Field(None, description='产物名称')
    artifact_path: str | None = Field(None, description='产物路径')
    summary_json: str | None = Field(None, description='产物摘要 (JSON)')
    sync_policy: str = Field(default='local_only', description='同步策略 (full/metadata_only/local_only)')


class CreateHasnSessionArtifactsParam(HasnSessionArtifactsSchemaBase):
    """创建 HASN 会话产物参数"""
    pass


class GetHasnSessionArtifactsDetail(HasnSessionArtifactsSchemaBase):
    """HASN 会话产物详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
