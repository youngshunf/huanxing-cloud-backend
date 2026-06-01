"""Agent 权限管理 Schema"""

from pydantic import Field

from backend.common.schema import SchemaBase


class AgentScopesConfig(SchemaBase):
    """Agent 权限配置（含三态 default_mode/capability_modes）"""

    scopes: list[str] = Field(default_factory=list, description='Agent 权限列表（审计快照）')
    post_needs_review: bool = Field(default=False, description='发帖是否需要审核')
    default_mode: str = Field(default='allow', description='默认模式 allow|ask|deny')
    capability_modes: dict[str, str] = Field(default_factory=dict, description='每能力 override {key: allow|ask|deny}')


class UpdateAgentScopesRequest(SchemaBase):
    """更新 Agent 权限请求（三态；scopes 为兼容字段，可选）"""

    default_mode: str = Field(default='allow', description='默认模式 allow|ask|deny')
    capability_modes: dict[str, str] = Field(default_factory=dict, description='每能力 override {key: allow|ask|deny}')
    post_needs_review: bool | None = Field(default=None, description='发帖是否需要审核（None 表示不改）')
    scopes: list[str] | None = Field(default=None, description='兼容字段，可选（审计快照）')


class UpdateAgentScopesResponse(SchemaBase):
    """更新 Agent 权限响应（D3 不重签 JWT，返回最新配置）"""

    config: AgentScopesConfig = Field(description='更新后的权限配置')


class ScopeCapability(SchemaBase):
    """catalog 单条能力（= 一个 scope）"""

    key: str = Field(description='能力 key（scope）')
    label: str = Field(description='中文显示名')
    domain: str = Field(default='', description='所属域')
    risk: str = Field(default='low', description='风险等级 low|medium|high（仅 UI 提示）')
    description: str = Field(default='', description='用途描述')
    mode: str = Field(description='当前三态 allow|ask|deny')
    tools: list[str] = Field(default_factory=list, description='覆盖的工具 canonical 名')


class ScopeSource(SchemaBase):
    """catalog 一个来源分组"""

    source: str = Field(description='来源 platform|app|external')
    label: str = Field(description='来源中文名')
    capabilities: list[ScopeCapability] = Field(default_factory=list)


class ScopeCatalogResponse(SchemaBase):
    """工具/scope 目录（按来源分组，每条带三态）"""

    default_mode: str = Field(default='allow')
    sources: list[ScopeSource] = Field(default_factory=list)
