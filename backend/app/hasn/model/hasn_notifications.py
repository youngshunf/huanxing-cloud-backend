from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText


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
