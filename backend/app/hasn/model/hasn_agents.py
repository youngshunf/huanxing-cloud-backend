from datetime import datetime
import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.dialects import postgresql

from backend.common.model import Base, id_key, UniversalText


class HasnAgents(Base):
    """HASN Agent 表（统一实体架构 v5.0）"""

    __tablename__ = 'hasn_agents'

    id: Mapped[id_key] = mapped_column(init=False)
    hasn_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='HASN Agent 唯一标识（格式: a_{uuid}）')
    star_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='Agent 唤星号（如: 100001#star）')
    owner_id: Mapped[str] = mapped_column(sa.String(40), default='', comment='所属 Human 的 hasn_id')
    name: Mapped[str] = mapped_column(sa.String(50), default='', comment='Agent 显示名')
    agent_name: Mapped[str] = mapped_column(sa.String(30), default='', comment='Agent 标识名')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Agent 描述')
    avatar_url: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='头像 URL')
    type: Mapped[str] = mapped_column(sa.String(20), default='', comment='Agent 类型 (desktop:桌面端:blue/mobile:手机端:green/cloud:云端:purple/web:网页端:orange)')
    role: Mapped[str] = mapped_column(sa.String(20), default='specialist', comment='Agent 角色 (primary:主要:blue/specialist:专家:green/service:服务:orange)')
    node_id: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='Agent 驻留节点 ID（设备指纹派生，格式: n_{hash}）')
    capabilities: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='Agent 能力列表（A2A AgentCard 兼容 JSONB）')
    api_key_hash: Mapped[str] = mapped_column(sa.String(64), default='', comment='Agent Key 的 SHA256 哈希')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态 (active:活跃:green/disabled:已停用:orange/deleted:已删除:red)')
    created_via: Mapped[str] = mapped_column(sa.String(20), default='', comment='创建来源 (guardian:Guardian注册:blue/client:客户端创建:green/ws:WS实时注册:purple)')
