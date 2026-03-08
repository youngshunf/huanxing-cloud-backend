"""
HASN 联系人关系表 (三维权限矩阵: relation_type × trust_level × scope)
对应设计文档: 06-数据模型.md §2.2
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HasnContact(Base):
    """HASN 联系人关系表 (三维权限矩阵)"""

    __tablename__ = 'hasn_contacts'

    id: Mapped[id_key] = mapped_column(init=False)

    # ── 关系双方 ──
    owner_id: Mapped[str] = mapped_column(
        sa.String(36), nullable=False,
        comment='关系拥有者 hasn_id',
    )
    peer_id: Mapped[str] = mapped_column(
        sa.String(36), nullable=False,
        comment='对方 hasn_id',
    )
    peer_type: Mapped[str] = mapped_column(
        sa.String(10), nullable=False,
        comment='对方类型: human / agent',
    )

    # ── 维度一: 关系类型 ──
    relation_type: Mapped[str] = mapped_column(
        sa.String(20), nullable=False, default='social',
        comment='关系类型: social/commerce/service/professional/platform',
    )

    # ── 维度二: 信任等级 ──
    trust_level: Mapped[int] = mapped_column(
        sa.SmallInteger, nullable=False, default=1,
        comment='信任等级: 0=blocked 1=stranger 2=normal 3=trusted 4=owner',
    )

    # ── 维度三: 作用域 (JSONB) ──
    scope: Mapped[dict | None] = mapped_column(
        JSONB, default=None,
        comment='关系作用域 (commerce/service/professional 各有不同结构)',
    )

    # ── 自定义权限覆盖 ──
    custom_permissions: Mapped[dict] = mapped_column(
        JSONB, default_factory=dict,
        comment='自定义权限覆盖',
    )

    # ── 社交附加信息 ──
    nickname: Mapped[str | None] = mapped_column(
        sa.String(100), default=None,
        comment='备注名',
    )
    tags: Mapped[list | None] = mapped_column(
        ARRAY(sa.String(200)), default=None,
        comment='分组标签',
    )
    subscription: Mapped[bool] = mapped_column(
        sa.Boolean, default=False,
        comment='是否订阅 (commerce: 新品推送)',
    )

    # ── 状态与请求 ──
    status: Mapped[str] = mapped_column(
        sa.String(20), default='pending',
        comment='状态: pending/connected/blocked/archived',
    )
    request_message: Mapped[str | None] = mapped_column(
        sa.Text, default=None,
        comment='好友请求附言',
    )

    # ── 过期 (service 关系订单完成后过期) ──
    auto_expire: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None,
        comment='自动过期时间',
    )

    # ── 互动统计 ──
    connected_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, init=False,
        comment='建立连接时间',
    )
    last_interaction_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, init=False,
        comment='最后互动时间',
    )
    interaction_count: Mapped[int] = mapped_column(
        sa.Integer, default=0,
        comment='互动次数',
    )

    __table_args__ = (
        # ⭐ 复合唯一键含 relation_type — 同一个 peer 可以有多种关系
        sa.UniqueConstraint('owner_id', 'peer_id', 'relation_type',
                            name='uq_hasn_contact_relation'),
        sa.Index('idx_contact_owner', 'owner_id'),
        sa.Index('idx_contact_peer', 'peer_id'),
        sa.Index('idx_contact_type', 'owner_id', 'relation_type'),
        sa.Index('idx_contact_level', 'owner_id', 'relation_type', 'trust_level'),
        sa.Index('idx_contact_status', 'status'),
        sa.Index('idx_contact_expire', 'auto_expire',
                 postgresql_where=sa.text("auto_expire IS NOT NULL")),
        sa.Index('idx_contact_subscription', 'owner_id',
                 postgresql_where=sa.text("subscription = TRUE")),
        {'comment': 'HASN 联系人关系表 (三维权限矩阵)'},
    )
