from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppScopes(Base):
    """应用权限定义表（{domain}.* namespace）"""

    __tablename__ = 'app_scopes'

    id: Mapped[id_key] = mapped_column(init=False)
    app_id: Mapped[str] = mapped_column(sa.String(255), default='', comment='关联的 App ID')
    scope: Mapped[str] = mapped_column(sa.String(255), default='', comment='权限标识，格式：{domain}.{resource}.{action}')
    display_name: Mapped[str] = mapped_column(sa.String(255), default='', comment='权限显示名称')
    description: Mapped[str] = mapped_column(UniversalText, default='', comment='权限描述')
    reason: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='为什么需要这个权限')
    risk_level: Mapped[str] = mapped_column(sa.String(20), default='', comment='风险等级 (low:低风险:green/medium:中风险:orange/high:高风险:red)')
    requires_owner_confirmation: Mapped[bool | None] = mapped_column(sa.BOOLEAN(), default=None, comment='是否需要 Owner 二次确认')
    rate_limit_per_minute: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='每分钟限流次数')
    rate_limit_per_hour: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='每小时限流次数')
    rate_limit_per_day: Mapped[int | None] = mapped_column(sa.INTEGER(), default=None, comment='每天限流次数')
