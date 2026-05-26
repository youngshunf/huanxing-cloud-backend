from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class MarketplaceDownloadHistory(Base):
    """技能市场下载历史表"""

    __tablename__ = 'marketplace_download_history'

    id: Mapped[id_key] = mapped_column(init=False)
    skill_id: Mapped[str] = mapped_column(sa.String(100), default='', comment='技能ID')
    version: Mapped[str] = mapped_column(sa.String(50), default='', comment='版本号')
    user_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='用户ID')
    ip_address: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='IP地址')
    user_agent: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='用户代理')
    downloaded_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='下载时间')
