from datetime import datetime
from uuid import UUID

import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone
from backend.utils.timezone import timezone


class HasnMessages(Base):
    """HASN 消息表"""

    __tablename__ = 'hasn_messages'

    id: Mapped[id_key] = mapped_column(init=False)
    conversation_id: Mapped[str | UUID] = mapped_column(sa.UUID(), default=None, comment='所属会话 ID')
    from_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='发送方 hasn_id')
    from_type: Mapped[int] = mapped_column(sa.SMALLINT(), default=0, comment='发送方类型 (1:人类/2:代理/3:系统)')
    to_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='接收方 hasn_id')
    to_type: Mapped[int] = mapped_column(sa.SMALLINT(), default=0, comment='接收方类型 (1:人类/2:代理/3:系统)')
    content_type: Mapped[int] = mapped_column(sa.SMALLINT(), default=0, comment='内容类型 (1:文本/2:图片/3:文件/4:语音/5:卡片/6:能力请求/7:能力响应)')
    content: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='消息内容 (JSON: {text/url/filename/...})')
    msg_type: Mapped[str] = mapped_column(sa.String(30), default='', comment='消息类型 (message:普通消息/contact_request:好友请求/contact_accept:接受好友/contact_reject:拒绝好友/notification:通知/system:系统消息)')
    status: Mapped[int] = mapped_column(sa.SMALLINT(), default=0, comment='消息状态 (1:已发送:blue/2:已送达:cyan/3:已读:green/4:已撤回:red)')
    priority: Mapped[str] = mapped_column(sa.String(10), default='', comment='优先级 (critical:紧急:red/high:高:orange/normal:普通:blue/low:低:gray)')
    reply_to_id: Mapped[int | None] = mapped_column(sa.BIGINT(), default=None, comment='回复的消息 ID')
    local_id: Mapped[str | UUID | None] = mapped_column(sa.UUID(), default=None, comment='客户端本地 ID (UUID, 用于去重)')
    context: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='消息上下文 (JSON: relation_type/scope/trade_session_id/thread_id 等)')
    recalled_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='撤回时间')
    recalled_by: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='撤回者 hasn_id')
    edited_at: Mapped[datetime | None] = mapped_column(TimeZone, default=None, comment='最后编辑时间')
    edit_version: Mapped[int] = mapped_column(sa.SMALLINT(), default=0, comment='编辑版本号')
    server_received_at: Mapped[datetime] = mapped_column(TimeZone, default_factory=timezone.now, comment='服务端接收时间')
