from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, TimeZone


class HasnSessions(Base):
    """HASN 会话分层 - 逻辑会话表"""

    __tablename__ = 'hasn_sessions'

    id: Mapped[str] = mapped_column(sa.String(40), primary_key=True, comment='会话 ID (ULID 格式)')
    conversation_id: Mapped[UUID | None] = mapped_column(sa.UUID(), default=None, comment='关联的 conversation ID')
    session_kind: Mapped[str] = mapped_column(sa.String(20), default='conversation', comment='会话类型 (conversation/task/temporary/external/system)')
    session_scope: Mapped[str] = mapped_column(sa.String(20), default='conversation_visible', comment='同步范围 (conversation_visible/summary_only/local_only)')
    session_status: Mapped[str] = mapped_column(sa.String(20), default='active', comment='会话状态 (active/paused/completed/archived)')
    origin_type: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='来源类型 (ui/scheduler/external_app/api/system)')
    origin_ref: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='来源引用 (task_id/app_id/trace_id)')
    parent_session_id: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='父会话 ID (用于分叉)')
    fork_point_message_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='分叉点消息 ID')
    summary_checkpoint_json: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='会话摘要检查点 (JSON)')
    last_message_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='最后一条消息 ID')
    last_message_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后消息时间')
    message_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='消息总数')
    created_time: Mapped[datetime] = mapped_column(TimeZone, default=datetime.now, comment='创建时间')
    updated_time: Mapped[datetime] = mapped_column(TimeZone, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class HasnSessionEvents(Base):
    """HASN 会话事件表"""

    __tablename__ = 'hasn_session_events'

    id: Mapped[int] = mapped_column(sa.BIGINT(), primary_key=True, autoincrement=True, comment='事件 ID')
    session_id: Mapped[str] = mapped_column(sa.String(40), nullable=False, comment='会话 ID')
    event_type: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment='事件类型 (session.created/session.paused/task.started/tool.called)')
    event_seq: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='会话内事件序号')
    payload_json: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='事件载荷 (JSON)')
    occurred_at: Mapped[datetime] = mapped_column(TimeZone, default=datetime.now, comment='事件发生时间')
    created_time: Mapped[datetime] = mapped_column(TimeZone, default=datetime.now, comment='创建时间')


class HasnSessionArtifacts(Base):
    """HASN 会话产物表"""

    __tablename__ = 'hasn_session_artifacts'

    id: Mapped[int] = mapped_column(sa.BIGINT(), primary_key=True, autoincrement=True, comment='产物 ID')
    session_id: Mapped[str] = mapped_column(sa.String(40), nullable=False, comment='会话 ID')
    artifact_kind: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment='产物类型 (file/code/report/data)')
    artifact_name: Mapped[str | None] = mapped_column(sa.String(200), default=None, comment='产物名称')
    artifact_path: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='产物路径')
    summary_json: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='产物摘要 (JSON)')
    sync_policy: Mapped[str] = mapped_column(sa.String(20), default='local_only', comment='同步策略 (full/metadata_only/local_only)')
    created_time: Mapped[datetime] = mapped_column(TimeZone, default=datetime.now, comment='创建时间')
