"""
HASN Human 用户表
对应设计文档: 06-数据模型.md §2.1 / 01-身份体系.md §二

⚠️ 字段顺序: 遵循 Python dataclass 规则 —— 无默认值的字段必须在有默认值之前
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base


class HasnHuman(Base):
    """HASN Human 用户表"""

    __tablename__ = 'hasn_humans'

    # ═══════════════════════════════════════
    # 无默认值字段 (必须排前面)
    # ═══════════════════════════════════════

    id: Mapped[str] = mapped_column(
        sa.String(36),
        primary_key=True,
        sort_order=-999,
        comment='hasn_id (h_uuid)',
    )
    star_id: Mapped[str] = mapped_column(
        sa.String(20), unique=True, nullable=False,
        comment='唤星号 (100001 / fuzi)',
    )
    name: Mapped[str] = mapped_column(
        sa.String(100), nullable=False,
        comment='昵称/显示名',
    )

    # ═══════════════════════════════════════
    # 有默认值字段
    # ═══════════════════════════════════════

    huanxing_user_id: Mapped[str | None] = mapped_column(
        sa.String(64), unique=True, default=None,
        comment='关联唤星平台 user_id',
    )
    bio: Mapped[str] = mapped_column(
        sa.Text, default='',
        comment='个人简介',
    )
    avatar_url: Mapped[str | None] = mapped_column(
        sa.String(500), default=None,
        comment='头像URL',
    )
    phone: Mapped[str | None] = mapped_column(
        sa.String(128), default=None,
        comment='手机号 (AES加密存储)',
    )
    phone_hash: Mapped[str | None] = mapped_column(
        sa.String(64), default=None, index=True,
        comment='手机号 SHA256 哈希 (用于搜索)',
    )
    profile: Mapped[dict] = mapped_column(
        JSONB, default_factory=dict,
        comment='完整 Profile Card (JSONB)',
    )
    privacy_rules: Mapped[dict] = mapped_column(
        JSONB, default_factory=dict,
        comment='隐私策略配置',
    )
    status: Mapped[str] = mapped_column(
        sa.String(20), default='active',
        comment='状态: active / suspended / deleted',
    )

    # ═══════════════════════════════════════
    # init=False 字段 (不参与构造函数，放最后)
    # ═══════════════════════════════════════

    last_online_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, init=False,
        comment='最后在线时间',
    )

    __table_args__ = (
        sa.Index('idx_human_star', 'star_id', unique=True),
        sa.Index('idx_human_phone_hash', 'phone_hash',
                 postgresql_where=sa.text("phone_hash IS NOT NULL")),
        sa.Index('idx_human_status', 'status'),
        sa.Index('idx_human_huanxing', 'huanxing_user_id',
                 postgresql_where=sa.text("huanxing_user_id IS NOT NULL")),
        {'comment': 'HASN Human 用户表'},
    )
