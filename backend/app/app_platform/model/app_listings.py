from datetime import datetime
from decimal import Decimal

from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppListings(Base):
    """应用市场列表表"""

    __tablename__ = 'app_listings'

    listing_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, default=None, comment='Listing ID')
    app_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    version_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment=None)
    visibility: Mapped[str] = mapped_column(sa.String(50), default='', comment='可见性 (private:私有:gray/public:公开:green)')
    title: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    description_long: Mapped[str] = mapped_column(UniversalText, default='', comment=None)
    pricing_model: Mapped[str] = mapped_column(sa.String(50), default='', comment='定价模式 (free:免费:green/one_time:一次性付费:blue/subscription:订阅:orange/usage_based:按量计费:purple)')
    price_amount: Mapped[Decimal | None] = mapped_column(sa.NUMERIC(), default=None, comment=None)
    install_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment=None)
    rating_average: Mapped[Decimal | None] = mapped_column(sa.NUMERIC(), default=None, comment=None)
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (draft:草稿:gray/pending_review:待审核:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/unlisted:已下架:orange)')
