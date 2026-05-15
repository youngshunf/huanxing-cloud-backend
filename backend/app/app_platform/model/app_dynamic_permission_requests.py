from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppDynamicPermissionRequests(Base):
    """动态权限请求表"""

    __tablename__ = 'app_dynamic_permission_requests'

    request_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, default=None, comment='请求 ID')
    installation_id: Mapped[str] = mapped_column(sa.String(255), default='', comment='关联的 Installation ID')
    scope: Mapped[str] = mapped_column(sa.String(255), default='', comment='请求的权限标识')
    requested_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='请求时间')
    request_reason: Mapped[str] = mapped_column(UniversalText, default='', comment='App 说明为什么需要这个权限')
    request_context: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='请求时的上下文信息（JSONB）')
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (pending:待处理:blue/approved:已批准:green/denied:已拒绝:red/expired:已过期:gray)')
    decided_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='决策时间')
    decided_by: Mapped[str | None] = mapped_column(sa.String(255), default=None, comment='决策者 Owner ID')
    decision_reason: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='决策理由')
    expires_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='请求过期时间（默认 24 小时）')
