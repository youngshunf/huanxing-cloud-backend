from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HasnCollections(Base):
    """社区收藏夹表"""

    __tablename__ = 'hasn_collections'

    id: Mapped[id_key] = mapped_column(init=False)
    collection_id: Mapped[str] = mapped_column(sa.String(40), default='', comment=None)
    owner_hasn_id: Mapped[str] = mapped_column(sa.String(40), default='', comment=None)
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment=None)
    is_public: Mapped[bool] = mapped_column(sa.BOOLEAN(), default=True, comment=None)
    item_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment=None)
    create_time: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment=None)
    update_time: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment=None)
