"""
HASN 通知队列表
对应设计文档: 06-数据模型.md §2.6
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HasnNotification(Base):
    """HASN 通知队列表"""

    __tablename__ = 'hasn_notifications'

    id: Mapped[id_key] = mapped_column(init=False)

    target_id: Mapped[str] = mapped_column(
        sa.String(36), nullable=False,
        comment='通知目标 hasn_id',
    )
    type: Mapped[str] = mapped_column(
        sa.String(30), nullable=False,
        comment='类型: contact_request/message_summary/event_reminder/system',
    )
    title: Mapped[str] = mapped_column(
        sa.String(200), nullable=False,
        comment='通知标题',
    )
    body: Mapped[str | None] = mapped_column(
        sa.Text, default=None,
        comment='通知正文',
    )
    data: Mapped[dict] = mapped_column(
        JSONB, default_factory=dict,
        comment='附加数据 (JSONB)',
    )
    read: Mapped[bool] = mapped_column(
        sa.Boolean, default=False,
        comment='是否已读',
    )

    __table_args__ = (
        sa.Index('idx_notif_target', 'target_id', 'read', 'created_time'),
        {'comment': 'HASN 通知队列表'},
    )
