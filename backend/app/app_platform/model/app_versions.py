from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppVersions(Base):
    """App 版本表"""

    __tablename__ = 'app_versions'

    version_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, default=None, comment='版本 ID')
    app_id: Mapped[str] = mapped_column(sa.String(255), default='', comment='App ID')
    version: Mapped[str] = mapped_column(sa.String(50), default='', comment='版本号')
    changelog: Mapped[str | None] = mapped_column(UniversalText, default=None, comment=None)
    manifest_snapshot: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='Manifest 快照（JSONB）')
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/deprecated:已废弃:orange)')
    published_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment=None)
