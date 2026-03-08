"""
HASN 群成员表
对应设计文档: 06-数据模型.md §2.3
"""
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HasnGroupMember(Base):
    """HASN 群成员表"""

    __tablename__ = 'hasn_group_members'

    id: Mapped[id_key] = mapped_column(init=False)

    conversation_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey('hasn_conversations.id', ondelete='CASCADE'),
        nullable=False,
        comment='群会话ID',
    )
    member_id: Mapped[str] = mapped_column(
        sa.String(36), nullable=False,
        comment='成员 hasn_id',
    )
    member_type: Mapped[str] = mapped_column(
        sa.String(10), nullable=False,
        comment='成员类型: human / agent',
    )
    member_star_id: Mapped[str] = mapped_column(
        sa.String(40), nullable=False,
        comment='成员唤星号',
    )
    member_name: Mapped[str] = mapped_column(
        sa.String(100), nullable=False,
        comment='成员名称(冗余，方便查询)',
    )
    role: Mapped[str] = mapped_column(
        sa.String(20), default='member',
        comment='角色: owner/admin/member',
    )
    muted: Mapped[bool] = mapped_column(
        sa.Boolean, default=False,
        comment='是否免打扰',
    )
    joined_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, init=False,
        comment='加入时间',
    )
    invited_by: Mapped[str | None] = mapped_column(
        sa.String(36), default=None,
        comment='邀请者 hasn_id',
    )

    __table_args__ = (
        sa.UniqueConstraint('conversation_id', 'member_id',
                            name='uq_hasn_group_member'),
        sa.Index('idx_group_member_conv', 'conversation_id'),
        sa.Index('idx_group_member_user', 'member_id'),
        {'comment': 'HASN 群成员表'},
    )
