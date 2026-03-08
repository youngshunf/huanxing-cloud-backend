"""
HASN 消息表
对应设计文档: 06-数据模型.md §2.3

⚠️ 字段顺序: 遵循 Python dataclass 规则 —— 无默认值的字段必须在有默认值之前
"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base


class HasnMessage(Base):
    """HASN 消息表"""

    __tablename__ = 'hasn_messages'

    # ═══════════════════════════════════════
    # init=False 主键
    # ═══════════════════════════════════════

    id: Mapped[int] = mapped_column(
        sa.BigInteger,
        primary_key=True,
        autoincrement=True,
        sort_order=-999,
        init=False,
        comment='消息ID (BIGINT 自增)',
    )

    # ═══════════════════════════════════════
    # 无默认值字段 (必须排前面)
    # ═══════════════════════════════════════

    conversation_id: Mapped[str] = mapped_column(
        sa.String(36), nullable=False, index=True,
        comment='会话ID (hasn_conversations.id)',
    )
    from_id: Mapped[str] = mapped_column(
        sa.String(36), nullable=False,
        comment='发送者 hasn_id (h_xxx 或 a_xxx)',
    )
    from_type: Mapped[int] = mapped_column(
        sa.SmallInteger, nullable=False,
        comment='发送者类型: 1=human 2=agent 3=system',
    )
    content: Mapped[str] = mapped_column(
        sa.Text, nullable=False,
        comment='消息内容 (纯文本直存，省JSON解析开销)',
    )

    # ═══════════════════════════════════════
    # 有默认值字段
    # ═══════════════════════════════════════

    content_type: Mapped[int] = mapped_column(
        sa.SmallInteger, nullable=False, default=1,
        comment='内容类型: 1=text 2=image 3=file 4=voice 5=rich 6=capability',
    )
    metadata_: Mapped[dict | None] = mapped_column(
        'metadata', JSONB, default=None,
        comment='可选元数据 (reply_to/capability/relation_type 等)',
    )
    reply_to: Mapped[int | None] = mapped_column(
        sa.BigInteger, default=None,
        comment='引用消息ID',
    )
    status: Mapped[int] = mapped_column(
        sa.SmallInteger, default=1,
        comment='状态: 1=sent 2=delivered 3=read 4=deleted',
    )

    __table_args__ = (
        sa.Index('idx_msg_conv_time', 'conversation_id', 'created_time'),
        sa.Index('idx_msg_undelivered', 'conversation_id', 'status',
                 postgresql_where=sa.text('status = 1')),
        {'comment': 'HASN 消息表 (MVP单表，后期按月分区)'},
    )
