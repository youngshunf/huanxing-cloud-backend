from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HasnSessions(Base):
    """HASN 会话分层 - 逻辑会话表"""

    __tablename__ = 'hasn_sessions'

    id: Mapped[id_key] = mapped_column(init=False)
    conversation_id: Mapped[str | UUID | None] = mapped_column(sa.UUID(), default=None, comment='关联的 conversation ID')
    session_kind: Mapped[str] = mapped_column(sa.String(20), default='', comment='会话类型 (conversation/task/temporary/external/system)')
    session_scope: Mapped[str] = mapped_column(sa.String(20), default='', comment='同步范围 (conversation_visible/summary_only/local_only)')
    session_status: Mapped[str] = mapped_column(sa.String(20), default='', comment='会话状态 (active/paused/completed/archived)')
    origin_type: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='来源类型 (ui/scheduler/external_app/api/system)')
    origin_ref: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment='来源引用 (task_id/app_id/trace_id)')
    parent_session_id: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='父会话 ID (用于分叉)')
    fork_point_message_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='分叉点消息 ID')
    summary_checkpoint_json: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='会话摘要检查点 (JSON)')
    last_message_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='最后一条消息 ID')
    last_message_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后消息时间')
    message_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='消息总数')
