from datetime import datetime
from decimal import Decimal

from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class AppEntitlements(Base):
    """App 购买凭证表"""

    __tablename__ = 'app_entitlements'

    entitlement_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, default=None, comment='凭证 ID')
    owner_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    listing_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment=None)
    installation_id: Mapped[str | None] = mapped_column(sa.String(255), default=None, comment=None)
    pricing_model: Mapped[str] = mapped_column(sa.String(50), default='', comment='定价模式 (free:免费:green/one_time:一次性:blue/subscription:订阅:orange/usage_based:按量:purple)')
    amount_paid: Mapped[Decimal | None] = mapped_column(sa.NUMERIC(), default=None, comment=None)
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (active:活跃:green/expired:已过期:gray/cancelled:已取消:orange/refunded:已退款:red/suspended:已暂停:red)')
    purchased_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment=None)
    expires_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment=None)
