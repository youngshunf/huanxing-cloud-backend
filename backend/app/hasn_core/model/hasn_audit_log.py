"""
HASN 审计日志表
对应设计文档: 06-数据模型.md §2.7
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HasnAuditLog(Base):
    """HASN 审计日志表"""

    __tablename__ = 'hasn_audit_log'

    id: Mapped[id_key] = mapped_column(init=False)

    actor_id: Mapped[str] = mapped_column(
        sa.String(36), nullable=False,
        comment='操作者 hasn_id',
    )
    actor_type: Mapped[str] = mapped_column(
        sa.String(10), nullable=False,
        comment='操作者类型: human/agent/system',
    )
    action: Mapped[str] = mapped_column(
        sa.String(50), nullable=False,
        comment='操作: register/login/send_message/add_contact/...',
    )
    target_type: Mapped[str | None] = mapped_column(
        sa.String(20), default=None,
        comment='目标类型',
    )
    target_id: Mapped[str | None] = mapped_column(
        sa.String(36), default=None,
        comment='目标ID',
    )
    details: Mapped[dict] = mapped_column(
        JSONB, default_factory=dict,
        comment='操作详情 (JSONB)',
    )
    ip_address: Mapped[str | None] = mapped_column(
        sa.String(45), default=None,
        comment='IP地址',
    )

    __table_args__ = (
        sa.Index('idx_audit_actor', 'actor_id', 'created_time'),
        sa.Index('idx_audit_action', 'action', 'created_time'),
        {'comment': 'HASN 审计日志表'},
    )
