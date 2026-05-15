from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppManifests(Base):
    """App 清单表"""

    __tablename__ = 'app_manifests'

    app_id: Mapped[str] = mapped_column(sa.String(255), primary_key=True, default='', comment='App ID')
    developer_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment='开发者 ID')
    namespace: Mapped[str] = mapped_column(sa.String(100), default='', comment=None)
    name: Mapped[str] = mapped_column(sa.String(100), default='', comment=None)
    display_name: Mapped[str] = mapped_column(sa.String(255), default='', comment='显示名称')
    description: Mapped[str] = mapped_column(UniversalText, default='', comment=None)
    icon_url: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment=None)
    current_version: Mapped[str] = mapped_column(sa.String(50), default='', comment=None)
    backend_runtime_mode: Mapped[str] = mapped_column(sa.String(50), default='', comment='后端运行模式 (platform_hosted:平台托管:blue/external_hosted:外部托管:green)')
    frontend_hosting_mode: Mapped[str] = mapped_column(sa.String(50), default='', comment='前端托管模式 (none:无前端:gray/platform_hosted:平台托管:blue/external_hosted:外部托管:green)')
    requested_scopes: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment=None)
    category: Mapped[str | None] = mapped_column(sa.String(100), default=None, comment=None)
    tags: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment=None)
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (draft:草稿:gray/submitted:已提交:blue/approved:已批准:green/rejected:已拒绝:red/published:已发布:green/archived:已归档:gray)')
