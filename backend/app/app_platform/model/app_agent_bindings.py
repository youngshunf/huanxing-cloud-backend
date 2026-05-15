from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class AppAgentBindings(Base):
    """Installation 绑定的 Agent 列表"""

    __tablename__ = 'app_agent_bindings'

    binding_id: Mapped[str | UUID] = mapped_column(sa.UUID(), primary_key=True, default=None, comment='绑定 ID')
    installation_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    agent_id: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    bound_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment=None)
    bound_by: Mapped[str] = mapped_column(sa.String(255), default='', comment=None)
    status: Mapped[str] = mapped_column(sa.String(50), default='', comment='状态 (active:生效:green/revoked:已撤销:red)')
