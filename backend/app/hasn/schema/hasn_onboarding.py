"""P0 HASN onboarding control-plane schemas.

These models mirror docs/openapi-hasn-cloud-v1.yaml for the S2 endpoints.
Do not add fields here unless the frozen OpenAPI contract changes.
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from backend.common.schema import CustomPhoneNumber, SchemaBase


class PhoneSendCodeRequest(SchemaBase):
    phone: CustomPhoneNumber = Field(description='手机号')
    purpose: Literal['login', 'bind_channel'] = Field(default='login', description='验证码用途')


class PhoneSendCodeResponse(SchemaBase):
    ok: bool = Field(description='验证码是否已发送；限流时为 false')
    retry_after_sec: int = Field(ge=0, description='再次发送前需要等待的秒数')


class PhoneVerifyRequest(SchemaBase):
    phone: CustomPhoneNumber = Field(description='手机号')
    code: str = Field(min_length=4, max_length=6, description='验证码')
    pending_intent_id: str | None = Field(default=None, description='反向 onboarding pending intent ID')


class PhoneVerifyResponse(SchemaBase):
    access_token: str = Field(description='HASN session access token')
    token_type: Literal['Bearer'] = Field(default='Bearer', description='Token 类型')
    expires_in_sec: int = Field(ge=1, description='访问令牌有效秒数')


class NodeClaim(SchemaBase):
    node_id: str = Field(description='HASN Node ID')
    device_name: str = Field(description='设备名称')
    platform: str = Field(description='设备平台')
    client_version: str | None = Field(default=None, description='客户端版本')


class ClientInfo(SchemaBase):
    protocol: str = Field(default='hasn/0.2', description='客户端协议版本')
    supported_extensions: list[str] | None = Field(default=None, description='支持的扩展列表')


class OnboardingEnsureRequest(SchemaBase):
    node: NodeClaim = Field(description='当前 hasn-node 声明')
    client: ClientInfo = Field(description='客户端能力摘要')
    pending_intent_id: str | None = Field(default=None, description='反向 onboarding pending intent ID')


class HumanSummary(SchemaBase):
    human_id: str = Field(description='Human HASN ID')
    owner_id: str = Field(description='Owner HASN ID')
    display_name: str | None = Field(default=None, description='显示名称')


class OwnerBindingSummary(SchemaBase):
    owner_id: str = Field(description='Owner HASN ID')
    node_id: str = Field(description='Node ID')
    status: Literal['active', 'expiring', 'revoked'] = Field(description='绑定状态')
    revision: int = Field(description='绑定修订号')


class AgentSummary(SchemaBase):
    agent_id: str = Field(description='默认 Agent ID')
    owner_id: str = Field(description='Owner HASN ID')
    hasn_id: str = Field(description='默认 Agent HASN ID')
    display_name: str | None = Field(default=None, description='默认 Agent 显示名称')


class SandboxSummary(SchemaBase):
    sandbox_id: str = Field(description='Sandbox ID')
    status: Literal['creating', 'active', 'sleeping', 'deleted', 'failed'] = Field(description='Sandbox 状态')
    base_url: str | None = Field(default=None, description='Tenant router base URL')


class OnboardingEnsureResponse(SchemaBase):
    human: HumanSummary = Field(description='Human / Owner 摘要')
    owner_binding: OwnerBindingSummary = Field(description='Node ↔ Owner 绑定摘要')
    default_agent: AgentSummary = Field(description='默认 Agent 摘要')
    sandbox: SandboxSummary | None = Field(default=None, description='Sandbox 路由摘要；S3 未创建时为空')
    sync_cursor: str = Field(description='bootstrap sync cursor')
