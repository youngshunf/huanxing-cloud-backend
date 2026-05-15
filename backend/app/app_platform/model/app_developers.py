from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class AppDevelopers(Base):
    """应用开发者表"""

    __tablename__ = 'app_developers'

    developer_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, default=None, comment='开发者 ID')
    owner_id: Mapped[str] = mapped_column(sa.String(255), default='', comment='关联的 Owner ID')
    display_name: Mapped[str] = mapped_column(sa.String(255), default='', comment='显示名称')
    email: Mapped[str] = mapped_column(sa.String(255), default='', comment='邮箱')
    company_name: Mapped[str | None] = mapped_column(sa.String(255), default=None, comment=None)
    website_url: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment=None)
    verification_status: Mapped[str] = mapped_column(sa.String(50), default='', comment='认证状态 (unverified:未认证:gray/pending:待审核:blue/verified:已认证:green/rejected:已拒绝:red)')
    verified_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment=None)
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (active:活跃:green/suspended:暂停:orange/banned:封禁:red)')
