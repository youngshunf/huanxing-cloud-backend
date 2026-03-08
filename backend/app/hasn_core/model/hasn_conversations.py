"""
HASN 对话/会话表
对应设计文档: 06-数据模型.md §2.3
"""
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base


class HasnConversation(Base):
    """HASN 对话/会话表"""

    __tablename__ = 'hasn_conversations'

    # ── 主键: UUID ──
    id: Mapped[str] = mapped_column(
        sa.String(36),
        primary_key=True,
        sort_order=-999,
        comment='会话ID (UUID)',
    )

    # ── 会话类型 ──
    type: Mapped[str] = mapped_column(
        sa.String(10), nullable=False,
        comment='类型: direct / group',
    )

    # ── 1v1 对话参与者 ──
    participant_a: Mapped[str | None] = mapped_column(
        sa.String(36), default=None,
        comment='参与者A hasn_id',
    )
    participant_b: Mapped[str | None] = mapped_column(
        sa.String(36), default=None,
        comment='参与者B hasn_id',
    )

    # ── 群聊字段 ──
    name: Mapped[str | None] = mapped_column(
        sa.String(100), default=None,
        comment='群名称',
    )
    group_star_id: Mapped[str | None] = mapped_column(
        sa.String(20), unique=True, default=None,
        comment='群唤星号 (g:500001)',
    )
    group_avatar: Mapped[str | None] = mapped_column(
        sa.String(500), default=None,
        comment='群头像',
    )
    group_description: Mapped[str | None] = mapped_column(
        sa.Text, default=None,
        comment='群描述',
    )
    agent_policy: Mapped[str] = mapped_column(
        sa.String(20), default='free',
        comment='Agent 发言策略: free/mention_only/silent/no_agent',
    )
    max_members: Mapped[int] = mapped_column(
        sa.Integer, default=500,
        comment='群最大成员数',
    )
    creator_id: Mapped[str | None] = mapped_column(
        sa.String(36), default=None,
        comment='群创建者 hasn_id',
    )

    # ── 通用字段 ──
    last_message_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, init=False,
        comment='最后消息时间',
    )
    last_message_preview: Mapped[str | None] = mapped_column(
        sa.Text, default=None, init=False,
        comment='最后消息预览',
    )
    message_count: Mapped[int] = mapped_column(
        sa.BigInteger, default=0,
        comment='消息总数',
    )
    status: Mapped[str] = mapped_column(
        sa.String(20), default='active',
        comment='状态: active / archived / deleted',
    )

    __table_args__ = (
        # 1v1 对话唯一约束: A→B 和 B→A 是同一个对话
        # 注意: 这种函数索引需要通过原生 SQL 迁移创建，这里仅做文档标记
        # CREATE UNIQUE INDEX idx_conv_direct ON hasn_conversations(
        #   LEAST(participant_a, participant_b), GREATEST(participant_a, participant_b))
        # WHERE type = 'direct';
        sa.Index('idx_conv_participant_a', 'participant_a',
                 postgresql_where=sa.text("type = 'direct'")),
        sa.Index('idx_conv_participant_b', 'participant_b',
                 postgresql_where=sa.text("type = 'direct'")),
        sa.Index('idx_conv_group_star', 'group_star_id',
                 postgresql_where=sa.text("group_star_id IS NOT NULL")),
        sa.Index('idx_conv_last_msg', 'last_message_at'),
        {'comment': 'HASN 对话/会话表'},
    )
