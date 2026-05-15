from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, UniversalText, TimeZone
from backend.utils.timezone import timezone


class AppPermissionAuditLogs(Base):
    """权限审计日志表"""

    __tablename__ = 'app_permission_audit_logs'

    id: Mapped[id_key] = mapped_column(init=False)
    owner_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='Owner ID')
    installation_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='Installation ID')
    app_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='App ID')
    agent_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Agent ID')
    action: Mapped[str] = mapped_column(sa.String(64), default='', comment='操作类型')
    scope: Mapped[str] = mapped_column(sa.String(255), default='', comment='权限 Scope')
    resource_type: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='资源类型')
    resource_id: Mapped[str | None] = mapped_column(sa.String(255), default=None, comment='资源 ID')
    result: Mapped[str] = mapped_column(sa.String(32), default='', comment='结果')
    error_message: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='错误信息')
    details: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='详细信息')
    request_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='请求 ID')
    user_agent: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='User Agent')
    ip_address: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='IP 地址')
