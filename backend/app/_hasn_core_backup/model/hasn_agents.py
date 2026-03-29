from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key, TimeZone


class HasnAgents(Base):
    """HASN Agent 表"""

    __tablename__ = 'hasn_agents'

    id: Mapped[id_key] = mapped_column(init=False)
    hasn_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='HASN Agent 唯一标识 (格式: a_{uuid})')
    star_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='Agent 唤星号 (如: 100001#star)')
    owner_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='所属 Human 的 hasn_id')
    name: Mapped[str] = mapped_column(sa.String(50), default='', comment='Agent 显示名')
    agent_name: Mapped[str] = mapped_column(sa.String(30), default='', comment='Agent 标识名')
    type: Mapped[str] = mapped_column(sa.String(20), default='cloud', comment='Agent 类型 (cloud:云端:blue/local:本地:green)')
    server_id: Mapped[str | None] = mapped_column(sa.String(50), default=None, comment='云端 Agent 所在服务器 ID')
    home_client_id: Mapped[int | None] = mapped_column(
        sa.BigInteger(), sa.ForeignKey('hasn_clients.id', ondelete='SET NULL'), default=None, comment='本地 Agent 归属客户端 ID'
    )
    api_key_hash: Mapped[str] = mapped_column(sa.String(64), default='', comment='API Key 的 SHA256 哈希')
    status: Mapped[str] = mapped_column(sa.String(20), default='active', comment='状态 (active:活跃:green/disabled:已停用:orange/revoked:已吊销:red)')
    created_via: Mapped[str] = mapped_column(sa.String(20), default='guardian', comment='创建来源 (guardian:Guardian注册:blue/client:客户端创建:green)')
