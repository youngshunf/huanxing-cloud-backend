from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppPermissionGrants(Base):
    """权限授予记录表"""

    __tablename__ = 'app_permission_grants'

    grant_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, init=False, server_default=sa.text('gen_random_uuid()'), comment='授权记录 ID')
    installation_id: Mapped[str] = mapped_column(sa.String(255), default='', comment='关联的 Installation ID')
    scope: Mapped[str] = mapped_column(sa.String(255), default='', comment='授予的权限标识')
    granted_by: Mapped[str] = mapped_column(sa.String(255), default='', comment='授予者 Owner ID')
    granted_at: Mapped[datetime] = mapped_column(TimeZone, init=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='授予时间')
    grant_source: Mapped[str] = mapped_column(sa.String(50), default='', comment='授予来源 (installation:安装时:blue/dynamic_request:动态请求:green/version_upgrade:版本升级:orange)')
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (active:生效:green/revoked:已撤销:red)')
    revoked_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='撤销时间')
    revoked_by: Mapped[str | None] = mapped_column(sa.String(255), default=None, comment='撤销者（owner 或 platform）')
    revocation_reason: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='撤销原因')
    last_used_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后使用时间')
    usage_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='使用次数')
