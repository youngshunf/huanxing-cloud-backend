from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, id_key
from backend.utils.timezone import timezone


class HasnAiNativeAppAudit(Base):
    """HASN AI-Native 运行时审计表"""

    __tablename__ = 'hasn_ai_native_app_audit'

    id: Mapped[id_key] = mapped_column(init=False)
    trace_id: Mapped[str] = mapped_column(sa.String(80), default='', comment='链路追踪 ID')
    step: Mapped[str] = mapped_column(sa.String(32), default='runtime', comment='审计步骤')
    workspace_kind: Mapped[str] = mapped_column(sa.String(16), default='personal', comment='workspace 类型')
    user_id: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, comment='个人空间用户 ID')
    enterprise_id: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, comment='企业 ID')
    app_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='应用 ID')
    app_version: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='应用版本')
    actor_type: Mapped[str] = mapped_column(sa.String(16), default='agent', comment='actor 类型')
    agent_hasn_id: Mapped[str | None] = mapped_column(sa.String(80), default=None, comment='Agent HASN ID')
    owner_hasn_id: Mapped[str | None] = mapped_column(sa.String(80), default=None, comment='Owner HASN ID')
    session_uuid: Mapped[str | None] = mapped_column(sa.String(80), default=None, comment='会话 UUID')
    method: Mapped[str] = mapped_column(sa.String(80), default='', comment='调用方法')
    capability_id: Mapped[str | None] = mapped_column(sa.String(120), default=None, comment='能力 ID')
    tool_id: Mapped[str | None] = mapped_column(sa.String(120), default=None, comment='Tool ID')
    event_type: Mapped[str | None] = mapped_column(sa.String(120), default=None, comment='事件类型')
    required_scopes: Mapped[list] = mapped_column(postgresql.JSONB(), default_factory=list, comment='必需 scopes')
    agent_scopes_snapshot: Mapped[list] = mapped_column(
        postgresql.JSONB(), default_factory=list, comment='Agent scopes 快照'
    )
    workspace_role: Mapped[str | None] = mapped_column(sa.String(16), default=None, comment='workspace 角色')
    risk_level: Mapped[str | None] = mapped_column(sa.String(16), default=None, comment='风险等级')
    decision: Mapped[str] = mapped_column(sa.String(32), default='', comment='allow/deny')
    confirmation_id: Mapped[str | None] = mapped_column(sa.String(80), default=None, comment='确认单 ID')
    result_ref: Mapped[str | None] = mapped_column(sa.String(255), default=None, comment='结果引用')
    error_code: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='错误码')
    context: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='额外上下文')
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
