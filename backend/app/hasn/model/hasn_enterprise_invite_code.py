from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, id_key
from backend.utils.timezone import timezone


class HasnEnterpriseInviteCode(Base):
    """企业邀请码"""

    __tablename__ = 'hasn_enterprise_invite_code'

    id: Mapped[id_key] = mapped_column(init=False)
    enterprise_id: Mapped[int] = mapped_column(sa.BigInteger(), default=0, comment='企业 ID')
    code: Mapped[str] = mapped_column(sa.String(32), default='', unique=True, comment='邀请码')
    created_by: Mapped[int] = mapped_column(sa.BigInteger(), default=0, comment='创建人')
    max_uses: Mapped[int | None] = mapped_column(sa.Integer(), default=None, comment='最大使用次数')
    used_count: Mapped[int] = mapped_column(sa.Integer(), default=0, comment='已使用次数')
    expires_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='过期时间')
    auto_approve: Mapped[bool] = mapped_column(sa.Boolean(), default=False, comment='是否自动审批')
    revoked: Mapped[bool] = mapped_column(sa.Boolean(), default=False, comment='是否撤销')
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
