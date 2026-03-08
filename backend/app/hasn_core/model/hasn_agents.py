"""
HASN Agent 表
对应设计文档: 06-数据模型.md §2.1 / 01-身份体系.md §二

⚠️ 字段顺序: 遵循 Python dataclass 规则 —— 无默认值的字段必须在有默认值之前
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base


class HasnAgent(Base):
    """HASN Agent 表"""

    __tablename__ = 'hasn_agents'

    # ═══════════════════════════════════════
    # 无默认值字段 (必须排前面)
    # ═══════════════════════════════════════

    id: Mapped[str] = mapped_column(
        sa.String(36),
        primary_key=True,
        sort_order=-999,
        comment='hasn_id (a_uuid)',
    )
    star_id: Mapped[str] = mapped_column(
        sa.String(40), unique=True, nullable=False,
        comment='Agent 唤星号 (100001#star)',
    )
    owner_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey('hasn_humans.id', ondelete='CASCADE'),
        nullable=False,
        comment='所属 Human 的 hasn_id',
    )
    name: Mapped[str] = mapped_column(
        sa.String(100), nullable=False,
        comment='Agent 显示名',
    )
    api_key_hash: Mapped[str] = mapped_column(
        sa.String(64), nullable=False,
        comment='API Key 的 SHA256 哈希',
    )
    api_key_prefix: Mapped[str] = mapped_column(
        sa.String(16), nullable=False,
        comment='API Key 前16字符 (用于显示)',
    )

    # ═══════════════════════════════════════
    # 有默认值字段
    # ═══════════════════════════════════════

    openclaw_agent_id: Mapped[str | None] = mapped_column(
        sa.String(64), default=None,
        comment='关联 OpenClaw Agent ID',
    )
    description: Mapped[str] = mapped_column(
        sa.Text, default='',
        comment='Agent 描述',
    )
    role: Mapped[str] = mapped_column(
        sa.String(20), default='primary',
        comment='角色: primary / specialist / service',
    )
    capabilities: Mapped[list] = mapped_column(
        JSONB, default_factory=list,
        comment='能力列表 (JSONB array)',
    )
    profile: Mapped[dict] = mapped_column(
        JSONB, default_factory=dict,
        comment='Agent Profile Card (JSONB)',
    )
    api_endpoint: Mapped[str | None] = mapped_column(
        sa.String(500), default=None,
        comment='外部 Agent 回调地址',
    )
    pricing: Mapped[dict] = mapped_column(
        JSONB, default_factory=dict,
        comment='定价信息',
    )
    reputation_score: Mapped[float] = mapped_column(
        sa.Numeric(3, 2), default=0.00,
        comment='综合评分 (0.00~5.00)',
    )
    review_count: Mapped[int] = mapped_column(
        sa.Integer, default=0,
        comment='评价总数',
    )
    total_interactions: Mapped[int] = mapped_column(
        sa.BigInteger, default=0,
        comment='交互总次数',
    )
    experience_credit_score: Mapped[float] = mapped_column(
        sa.Numeric(5, 2), default=0.00,
        comment='经验贡献信用分',
    )
    experience_shared_count: Mapped[int] = mapped_column(
        sa.Integer, default=0,
        comment='分享的经验总数',
    )
    experience_adopted_count: Mapped[int] = mapped_column(
        sa.Integer, default=0,
        comment='经验被采纳总次数',
    )
    status: Mapped[str] = mapped_column(
        sa.String(20), default='active',
        comment='状态: active / disabled / revoked / deleted',
    )

    # ═══════════════════════════════════════
    # init=False 字段 (不参与构造函数，放最后)
    # ═══════════════════════════════════════

    last_active_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, init=False,
        comment='最后活跃时间',
    )

    __table_args__ = (
        sa.Index('idx_agent_star', 'star_id', unique=True),
        sa.Index('idx_agent_owner', 'owner_id'),
        sa.Index('idx_agent_role', 'role'),
        sa.Index('idx_agent_status', 'status'),
        sa.Index('idx_agent_rating', 'reputation_score',
                 postgresql_where=sa.text("status = 'active'")),
        sa.Index('idx_agent_openclaw', 'openclaw_agent_id',
                 postgresql_where=sa.text("openclaw_agent_id IS NOT NULL")),
        {'comment': 'HASN Agent 表'},
    )
