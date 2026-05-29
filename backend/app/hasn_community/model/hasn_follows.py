from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HasnFollows(Base):
    """社区关注表"""

    __tablename__ = 'hasn_follows'

    id: Mapped[id_key] = mapped_column(init=False)
    follower_hasn_id: Mapped[str] = mapped_column(sa.String(40), default='', comment=None)
    target_type: Mapped[str] = mapped_column(sa.String(10), default='', comment='human / agent / topic')
    target_hasn_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='被关注对象的 hasn_id 或 topic 标识')
    created_time: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment=None)
