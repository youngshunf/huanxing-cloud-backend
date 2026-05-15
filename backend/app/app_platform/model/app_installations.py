from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class AppInstallations(Base):
    """App 安装记录表"""

    __tablename__ = 'app_installations'

    installation_id: Mapped[str] = mapped_column(sa.String(255), primary_key=True, default='', comment='Installation ID')
    owner_id: Mapped[str] = mapped_column(sa.String(255), default='', comment='Owner ID')
    app_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    listing_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment=None)
    installed_version: Mapped[str] = mapped_column(sa.String(50), default='', comment=None)
    granted_scopes: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='授予的权限列表（JSONB）')
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (active:活跃:green/update_available:有更新:blue/pending_reauth:待重新授权:orange/suspended:已暂停:red/revoked:已撤销:red)')
    installed_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment=None)
    last_used_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment=None)
