from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, id_key
from backend.utils.timezone import timezone


class HasnWorkspaceApp(Base):
    """工作空间挂载的应用"""

    __tablename__ = 'hasn_workspace_app'

    id: Mapped[id_key] = mapped_column(init=False)
    workspace_kind: Mapped[str] = mapped_column(
        sa.String(16), default='personal', comment='类型 (personal:个人:gray/enterprise:企业:purple)'
    )
    user_id: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, comment='个人空间用户 ID')
    enterprise_id: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, comment='企业空间 ID')
    app_id: Mapped[str] = mapped_column(sa.String(64), default='', comment='应用 ID')
    status: Mapped[str] = mapped_column(
        sa.String(16), default='active', comment='状态 (active:启用:green/disabled:停用:gray)'
    )
    config: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='应用配置')
    enabled_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='启用时间')
    enabled_by: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, comment='启用人')
