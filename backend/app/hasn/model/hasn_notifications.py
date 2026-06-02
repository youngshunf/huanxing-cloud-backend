import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class HasnNotifications(Base):
    """HASN 通知队列表"""

    __tablename__ = 'hasn_notifications'

    id: Mapped[id_key] = mapped_column(init=False)
    target_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='通知目标（接收方）hasn_id')
    type: Mapped[str] = mapped_column(sa.String(30), default='', comment='通知类型 (contact_request:好友请求:blue/contact_accepted:好友接受:green/message_summary:消息摘要:cyan/event_reminder:事件提醒:orange/system:系统通知:gray)')
    title: Mapped[str] = mapped_column(sa.String(200), default='', comment='通知标题')
    body: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='通知正文')
    data: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='附加数据 (JSONB)')
    read: Mapped[bool] = mapped_column(sa.BOOLEAN(), default=True, comment='是否已读')
    # --- 统一通知服务超集（2026-06-02 additive，§4.1）---
    category: Mapped[str] = mapped_column(sa.String(20), default='system', comment='通知粗类（定默认投递策略与默认优先级）')
    priority: Mapped[str] = mapped_column(sa.String(10), default='normal', comment='优先级 critical|high|normal|low')
    source: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='发送主体 NotificationSource')
    dedupe_key: Mapped[str | None] = mapped_column(sa.String(120), default=None, comment='去重键')
    group_key: Mapped[str | None] = mapped_column(sa.String(120), default=None, comment='聚合键（默认 type 冒号 target_id）')
    delivery: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='投递策略落地结果')
    state: Mapped[str] = mapped_column(sa.String(12), default='unread', comment='状态 unread|read|archived')
