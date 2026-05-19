from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone
from backend.utils.timezone import timezone


class HasnUserActiveWorkspace(Base):
    """每账号当前活跃工作区"""

    __tablename__ = 'hasn_user_active_workspace'

    user_id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True, default=0, comment='用户 ID')
    kind: Mapped[str] = mapped_column(
        sa.String(16), default='personal', comment='类型 (personal:个人:gray/enterprise:企业:purple)'
    )
    enterprise_id: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, comment='企业 ID')
    switched_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='切换时间')
