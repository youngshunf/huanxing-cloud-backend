from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, TimeZone


class HasnConversations(Base):
    """HASN 会话表"""

    __tablename__ = 'hasn_conversations'

    # UUID 主键
    id: Mapped[str] = mapped_column(sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()'), init=False, comment='会话 ID (UUID)')
    # 无默认值字段排前面
    participant_a_id: Mapped[str] = mapped_column(sa.String(40), comment='参与方 A 的 hasn_id')
    # 有默认值字段排后面
    type: Mapped[str] = mapped_column(sa.String(10), default='direct', comment='会话类型: direct/group')
    relation_type: Mapped[str | None] = mapped_column(sa.String(20), default='social', comment='关系类型: social/commerce/service/professional/platform')
    participant_b_id: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='参与方 B 的 hasn_id (群聊为 NULL)')
    participant_a_type: Mapped[str] = mapped_column(sa.String(10), default='human', comment='参与方 A 类型: human/agent')
    participant_b_type: Mapped[str | None] = mapped_column(sa.String(10), default='human', comment='参与方 B 类型: human/agent')
    trade_session_id: Mapped[str | None] = mapped_column(sa.UUID(), default=None, comment='关联交易会话 ID')
    last_message_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='最后一条消息 ID')
    last_message_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后消息时间')
    last_message_preview: Mapped[str | None] = mapped_column(sa.String(200), default=None, comment='最后消息预览')
    last_message_from: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='最后消息发送方 hasn_id')
    message_count: Mapped[int] = mapped_column(sa.INTEGER(), default=0, comment='消息总数')
