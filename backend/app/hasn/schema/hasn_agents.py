from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnAgentsSchemaBase(SchemaBase):
    """HASN Agent 基础模型"""
    hasn_id: str = Field(description='HASN Agent 唯一标识（格式: a_{uuid}）')
    star_id: str = Field(description='Agent 唤星号（如: 100001#star）')
    owner_id: str = Field(description='所属 Human 的 hasn_id')
    display_name: str = Field(description='Agent 显示名（支持中文，对外展示）')
    agent_name: str = Field(description='Agent 标识名')
    description: str | None = Field(None, description='Agent 描述')
    avatar: str | None = Field(None, description='头像（与 sys_user.avatar 对齐）')
    type: str = Field(description='Agent 类型 (desktop:桌面端:blue/mobile:手机端:green/cloud:云端:purple/web:网页端:orange)')
    role: str = Field(description='Agent 角色 (primary:主要:blue/specialist:专家:green/service:服务:orange)')
    node_id: str | None = Field(None, description='Agent 驻留节点 ID（设备指纹派生）')
    home_client_id: int | None = Field(None, description='本地 Agent 归属客户端 ID')
    template_id: str | None = Field(None, description='Agent 模板 ID')
    skills: dict[str, Any] | list[Any] | None = Field(None, description='Agent 技能配置 JSON')
    soul_md: str | None = Field(None, description='Agent SOUL.md 内容')
    user_md: str | None = Field(None, description='Agent USER.md 内容')
    profile_source: str = Field(default='cloud', description='Profile 来源')
    profile_revision: int = Field(default=1, description='Agent Profile 修订号')
    api_key_hash: str = Field(description='API Key 的 SHA256 哈希')
    status: str = Field(description='状态 (active:活跃:green/disabled:已停用:orange/revoked:已吊销:red)')
    created_via: str = Field(description='创建来源 (guardian:Guardian注册:blue/client:客户端创建:green)')
    social_enabled: bool = Field(default=False, description='是否对外开启社交可见')


class CreateHasnAgentsParam(HasnAgentsSchemaBase):
    """创建HASN Agent 参数"""


class UpdateHasnAgentsParam(HasnAgentsSchemaBase):
    """更新HASN Agent 参数"""


class DeleteHasnAgentsParam(SchemaBase):
    """删除HASN Agent 参数"""

    pks: list[int] = Field(description='HASN Agent  ID 列表')


class GetHasnAgentsDetail(HasnAgentsSchemaBase):
    """HASN Agent 详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None


class AgentSnapshot(SchemaBase):
    """云端 Agent Profile 快照，本地 hasn-node 以此为 Profile 事实源。"""

    hasn_id: str = Field(description='HASN Agent ID')
    star_id: str = Field(description='Agent 唤星号')
    owner_id: str = Field(description='所属 Human hasn_id')
    agent_name: str = Field(description='Agent 英文/目录标识')
    display_name: str = Field(description='Agent 显示名')
    description: str | None = Field(None, description='Agent 简介')
    avatar: str | None = Field(None, description='Agent 头像')
    type: str = Field(default='desktop', description='Agent 类型')
    role: str = Field(default='specialist', description='Agent 角色')
    node_id: str | None = Field(None, description='驻留节点 ID 摘要')
    capabilities: dict[str, Any] | list[Any] | None = Field(None, description='能力摘要')
    template_id: str | None = Field(None, description='模板 ID')
    skills: dict[str, Any] | list[Any] | None = Field(None, description='技能配置')
    soul_md: str | None = Field(None, description='SOUL.md 内容')
    user_md: str | None = Field(None, description='USER.md 内容')
    profile_revision: int = Field(default=1, description='Profile 修订号')
    status: str = Field(default='active', description='Agent 状态')
    social_enabled: bool = Field(default=False, description='是否对外开启社交可见')
    updated_time: datetime | None = Field(None, description='更新时间')


class CloudCreateAgentRequest(SchemaBase):
    """hasn-node/WebUI 发起的云端优先 Agent 创建请求。"""

    owner_id: str = Field(description='Owner HASN ID')
    template_id: str | None = Field(None, description='模板 ID；空表示自定义')
    agent_name: str | None = Field(None, description='Agent 英文/目录标识；空则云端按显示名/模板生成')
    display_name: str = Field(description='Agent 显示名')
    description: str | None = Field(None, description='Agent 简介')
    avatar: str | None = Field(None, description='Agent 头像 URL')
    skills: dict[str, Any] | list[Any] | None = Field(None, description='技能配置')
    soul_md: str | None = Field(None, description='SOUL.md 内容')
    user_md: str | None = Field(None, description='USER.md 内容')
    runtime_type: str | None = Field(None, description='期望本地绑定 Runtime 类型')
    node_id: str | None = Field(None, description='创建发起节点 ID')
    agent_type: str = Field(default='desktop', description='Agent 类型')
    role: str = Field(default='specialist', description='Agent 角色')
    capabilities: dict[str, Any] | list[Any] | None = Field(None, description='能力摘要')


class AgentTokenInfo(SchemaBase):
    """Agent JWT 信息"""
    access_token: str = Field(description='Agent JWT')
    scopes: list[str] = Field(description='Agent 权限列表')


class CloudCreateAgentResponse(SchemaBase):
    agent: AgentSnapshot = Field(description='云端 Agent 快照')
    agent_key: str | None = Field(None, description='新建 Agent Key，仅创建时返回')
    agent_token: AgentTokenInfo | None = Field(None, description='Agent JWT，仅创建时返回')
    already_exists: bool = Field(default=False, description='是否幂等命中已有 Agent')


class AgentSyncRequest(SchemaBase):
    owner_id: str = Field(description='Owner HASN ID')
    after_revision: int | None = Field(None, ge=0, description='仅返回大于该 Profile revision 的 Agent')
    include_disabled: bool = Field(default=True, description='是否返回停用/删除态 Agent')


class AgentSyncResponse(SchemaBase):
    owner_id: str = Field(description='Owner HASN ID')
    server_revision: int = Field(ge=0, description='当前最大 Profile revision')
    agents: list[AgentSnapshot] = Field(default_factory=list, description='Agent 快照列表')
