import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HasnNotificationPreferences(Base):
    """HASN 主人通知偏好表"""

    __tablename__ = 'hasn_notification_preferences'

    id: Mapped[id_key] = mapped_column(init=False)
    owner_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='主人 hasn_id')
    category: Mapped[str] = mapped_column(sa.String(20), default='*', comment='通知粗类，或 * 表全局默认')
    channels: Mapped[dict] = mapped_column(
        postgresql.JSONB(), default_factory=dict, comment='渠道开关 {center,card_message,toast,push}'
    )
    dnd: Mapped[dict] = mapped_column(
        postgresql.JSONB(), default_factory=dict, comment='免打扰 {enabled,start,end,tz,allow_critical}'
    )
