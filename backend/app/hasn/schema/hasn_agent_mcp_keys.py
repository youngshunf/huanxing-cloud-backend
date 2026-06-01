from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnAgentMcpKeysSchemaBase(SchemaBase):
    """Agent MCP 接入凭证基础模型"""

    agent_hasn_id: str = Field(description='归属 Agent 的 HASN ID')
    owner_hasn_id: str = Field(description='主人 HASN ID')
    owner_user_id: int | None = Field(None, description='主人 sys_user.id')
    key_prefix: str = Field(description='明文前缀（展示/审计用，不可反推完整 key）')
    scopes: list[str] = Field(default_factory=list, description='scope 集（与 Agent JWT 同语义的字符串数组）')
    node_id: str | None = Field(None, description='设备绑定 node_id（空=不限设备；默认签发即绑当前 node）')
    status: str = Field(description='状态 (active:启用:green/revoked:已吊销:red)')
    expire_time: datetime | None = Field(None, description='过期时间（空=不过期，生命周期靠吊销/轮换管理）')
    last_used_time: datetime | None = Field(None, description='最近使用时间（审计 / 可疑使用排查）')


class IssueAgentMcpKeyParam(SchemaBase):
    """签发 Agent MCP 接入凭证参数（owner 端发起，owner 身份由 JWT 解析，不在入参里）"""

    agent_hasn_id: str = Field(description='为哪个 Agent 签发（须属于当前 owner）')
    scopes: list[str] = Field(default_factory=list, description='scope 集（缺省=空，按需授予）')
    node_id: str | None = Field(None, description='设备绑定 node_id（缺省=由签发上下文绑定/不限）')
    expire_time: datetime | None = Field(None, description='可选过期时间（缺省=不过期，靠吊销/轮换管理）')


class IssuedAgentMcpKey(SchemaBase):
    """签发结果：完整明文 key 仅在此返回一次，之后只存哈希"""

    id: int
    agent_hasn_id: str
    owner_hasn_id: str
    key_prefix: str = Field(description='明文前缀（展示/审计用）')
    key: str = Field(description='完整明文 key，仅签发时返回一次，请立即妥善保存')
    scopes: list[str] = Field(default_factory=list)
    node_id: str | None = None
    status: str
    expire_time: datetime | None = None
    created_time: datetime


class AgentMcpKeyInfo(SchemaBase):
    """凭证信息（列表/详情；不含明文、不含 key_hash）"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_hasn_id: str
    owner_hasn_id: str
    key_prefix: str
    scopes: list[str] = Field(default_factory=list)
    node_id: str | None = None
    status: str
    expire_time: datetime | None = None
    last_used_time: datetime | None = None
    created_time: datetime
    updated_time: datetime | None = None
