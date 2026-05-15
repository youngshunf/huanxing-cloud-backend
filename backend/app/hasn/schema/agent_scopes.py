"""Agent 权限管理 Schema"""

from pydantic import Field

from backend.common.schema import SchemaBase


class AgentScopesConfig(SchemaBase):
    """Agent 权限配置"""

    scopes: list[str] = Field(description='Agent 权限列表')
    post_needs_review: bool = Field(default=False, description='发帖是否需要审核')


class UpdateAgentScopesRequest(SchemaBase):
    """更新 Agent 权限请求"""

    scopes: list[str] = Field(description='Agent 权限列表')
    post_needs_review: bool = Field(default=False, description='发帖是否需要审核')


class AgentTokenInfo(SchemaBase):
    """Agent JWT 信息"""

    access_token: str = Field(description='Agent JWT')
    scopes: list[str] = Field(description='Agent 权限列表')


class UpdateAgentScopesResponse(SchemaBase):
    """更新 Agent 权限响应"""

    agent_token: AgentTokenInfo = Field(description='新签发的 Agent JWT')
