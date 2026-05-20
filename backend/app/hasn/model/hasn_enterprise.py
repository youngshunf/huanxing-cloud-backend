from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone, UniversalText, id_key
from backend.utils.timezone import timezone


class HasnEnterprise(Base):
    """企业实体"""

    __tablename__ = 'hasn_enterprise'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(128), default='', comment='企业名称')
    slug: Mapped[str] = mapped_column(sa.String(64), default='', unique=True, comment='企业唯一标识')
    logo: Mapped[str | None] = mapped_column(sa.String(512), default=None, comment='企业 Logo')
    industry: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='所属行业')
    company_size: Mapped[str | None] = mapped_column(sa.String(32), default=None, comment='企业规模')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='企业描述')
    owner_user_id: Mapped[int] = mapped_column(sa.BigInteger(), default=0, comment='企业所有者 sys_user.id')
    join_policy: Mapped[str] = mapped_column(
        sa.String(16),
        default='invite_only',
        comment='加入策略 (invite_only:仅邀请码:blue/open:开放申请:green/closed:关闭:gray)',
    )
    status: Mapped[str] = mapped_column(
        sa.String(16),
        default='active',
        comment='状态 (active:正常:green/suspended:已暂停:orange/deleted:已注销:red)',
    )
    created_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='更新时间')
