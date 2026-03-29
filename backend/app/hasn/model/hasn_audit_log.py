from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class HasnAuditLog(Base):
    """HASN 审计日志表"""

    __tablename__ = 'hasn_audit_log'

    id: Mapped[id_key] = mapped_column(init=False)
    actor_id: Mapped[str] = mapped_column(sa.String(36), default='', comment='操作者 hasn_id')
    actor_type: Mapped[str] = mapped_column(sa.String(10), default='', comment='操作者类型 (human:人类:blue/agent:代理:green/system:系统:gray)')
    action: Mapped[str] = mapped_column(sa.String(50), default='', comment='操作类型 (register:注册:blue/login:登录:green/send_message:发消息:cyan/add_contact:加好友:orange/block_contact:拉黑:red/create_agent:创建Agent:purple/delete_agent:删除Agent:red/bind_client:绑定客户端:green/unbind_client:解绑客户端:orange)')
    target_type: Mapped[str | None] = mapped_column(sa.String(20), default=None, comment='目标类型 (human:人类:blue/agent:代理:green/client:客户端:orange/conversation:会话:cyan/message:消息:purple)')
    target_id: Mapped[str | None] = mapped_column(sa.String(36), default=None, comment='目标 ID')
    details: Mapped[dict] = mapped_column(postgresql.JSONB(), default_factory=dict, comment='操作详情 (JSONB)')
    ip_address: Mapped[str | None] = mapped_column(sa.String(45), default=None, comment='IP 地址')
