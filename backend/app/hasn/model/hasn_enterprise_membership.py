from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, UniversalText, id_key
from backend.utils.timezone import timezone


class HasnEnterpriseMembership(Base):
    """企业成员关系与申请记录"""

    __tablename__ = 'hasn_enterprise_membership'

    id: Mapped[id_key] = mapped_column(init=False)
    enterprise_id: Mapped[int] = mapped_column(sa.BigInteger(), default=0, comment='企业 ID')
    user_id: Mapped[int] = mapped_column(sa.BigInteger(), default=0, comment='用户 ID')
    role: Mapped[str] = mapped_column(
        sa.String(16), default='member', comment='角色 (owner:所有者:purple/admin:管理员:blue/member:成员:green)'
    )
    status: Mapped[str] = mapped_column(
        sa.String(16),
        default='pending',
        comment='状态 (pending:待审批:orange/approved:已通过:green/rejected:已拒绝:red/left:已退出:gray/removed:已移除:gray)',
    )
    apply_message: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='申请说明')
    apply_via: Mapped[str | None] = mapped_column(sa.String(16), default=None, comment='申请来源')
    invite_code: Mapped[str | None] = mapped_column(sa.String(32), default=None, comment='邀请码')
    decided_by: Mapped[int | None] = mapped_column(sa.BigInteger(), default=None, comment='审批人')
    decided_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='审批时间')
    decision_note: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='审批备注')
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='更新时间')
