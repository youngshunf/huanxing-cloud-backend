from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class HxCreatorHotTopic(Base):
    """热榜快照表"""

    __tablename__ = 'hx_creator_hot_topic'

    id: Mapped[id_key] = mapped_column(init=False)
    platform_id: Mapped[str] = mapped_column(sa.String(50), default='', comment='平台标识')
    platform_name: Mapped[str] = mapped_column(sa.String(50), default='', comment='平台名称')
    title: Mapped[str] = mapped_column(sa.String(200), default='', comment='热点标题')
    url: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='热点链接')
    rank: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='排名')
    heat_score: Mapped[float | None] = mapped_column(sa.REAL(), default=None, comment='热度分数')
    fetch_source: Mapped[str] = mapped_column(sa.String(50), default='', comment='数据来源')
    fetched_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='抓取时间')
    batch_date: Mapped[str] = mapped_column(sa.String(10), default='', comment='批次日期')
