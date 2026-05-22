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
    display_name: Mapped[str] = mapped_column(sa.String(100), default='', comment='Agent 显示名（支持中文，对外展示）')
    agent_name: Mapped[str] = mapped_column(sa.String(30), default='', comment='Agent 标识名')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Agent 描述')
    avatar: Mapped[str | None] = mapped_column(sa.String(500), default=None, comment='头像（与 sys_user.avatar 对齐）')
    type: Mapped[str] = mapped_column(sa.String(20), default='', comment='Agent 类型 (desktop:桌面端:blue/mobile:手机端:green/cloud:云端:purple/web:网页端:orange)')
    role: Mapped[str] = mapped_column(sa.String(20), default='specialist', comment='Agent 角色 (primary:主要:blue/specialist:专家:green/service:服务:orange)')
    node_id: Mapped[str | None] = mapped_column(sa.String(40), default=None, comment='Agent 驻留节点 ID（设备指纹派生，格式: n_{hash}）')
    capabilities: Mapped[dict | None] = mapped_column(postgresql.JSONB(), default=None, comment='Agent 能力列表（A2A AgentCard 兼容 JSONB）')
    template_id: Mapped[str | None] = mapped_column(sa.String(80), default=None, comment='Agent 模板 ID（来自 Agent 市场，可空表示自定义）')
    skills: Mapped[dict | list | None] = mapped_column(postgresql.JSONB(), default=None, comment='Agent 技能配置 JSON（云端 Profile 配置源）')
    soul_md: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Agent SOUL.md 内容（云端 Profile 配置源）')
    user_md: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='Agent USER.md 内容（云端 Profile 配置源）')
    profile_source: Mapped[str] = mapped_column(sa.String(20), default='cloud', comment='Profile 来源 (cloud:云端事实源:green/imported:导入:blue)')
    profile_revision: Mapped[int] = mapped_column(sa.BigInteger, default=1, comment='Agent Profile 修订号')
    api_key_hash: Mapped[str] = mapped_column(sa.String(64), default='', comment='Agent Key 的 SHA256 哈希')
    tags: Mapped[list | None] = mapped_column(postgresql.JSONB(), default=list, comment='Agent 标签数组（云端权威，daemon 仅镜像）')
    capability_set_id: Mapped[str | None] = mapped_column(sa.String(80), default=None, comment='Agent 能力集 ID（与 hasn_agent_capabilities 关联，云端权威）')
    persona_ref: Mapped[str | None] = mapped_column(sa.String(120), default=None, comment='Agent persona 引用（template / persona 资产 ID，云端权威）')
    status: Mapped[str] = mapped_column(sa.String(20), default='', comment='状态/生命周期 (active:活跃:green/disabled:已停用:orange/revoked:已吊销:red/archived:已归档:gray/deleted:已删除:gray)')
    created_via: Mapped[str] = mapped_column(sa.String(20), default='', comment='创建来源 (guardian:Guardian注册:blue/client:客户端创建:green/ws:WS实时注册:purple)')
    social_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False, comment='是否对外开启社交可见 (true:社交可见/false:仅自用)')
    binding_node_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, comment='Agent 当前绑定的 node ID')
    binding_status: Mapped[str] = mapped_column(sa.String(32), default='unbound', comment='binding 状态 (unbound:未绑定:gray/binding:绑定中:blue/bound:已绑定:green/failed:绑定失败:red)')
    binding_updated_at: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, comment='binding 状态更新时间（Unix 秒）')
    deleted_at: Mapped[datetime | None] = mapped_column(default=None, comment='软删除时间')
