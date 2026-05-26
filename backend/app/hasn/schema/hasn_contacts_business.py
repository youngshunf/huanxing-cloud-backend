"""
HASN 联系人业务 Schema
对应设计文档: 07-API设计.md §三
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# 从 constants 导入六级标签（统一数据源）
from backend.app.hasn.constants import TRUST_LEVEL_LABELS as _TRUST_LEVEL_LABELS

# 兼容旧导入路径
TRUST_LEVEL_LABELS = _TRUST_LEVEL_LABELS


class HasnContactPeerOut(BaseModel):
    hasn_id: str
    star_id: str
    name: str
    type: str  # human / agent
    avatar: str | None = None
    status: str = 'active'


class HasnContactRequestReq(BaseModel):
    """发送好友请求"""
    target_star_id: str = Field(..., description='目标唤星号')
    message: str = Field('', description='请求附言')


class HasnContactRespondReq(BaseModel):
    """回应好友请求"""
    action: str = Field(..., description='accept / reject')
    reason: str | None = None


class HasnContactRequestOut(BaseModel):
    request_id: int
    status: str
    created_at: datetime | None = None
    relation_type: str = 'social'
    target: HasnContactPeerOut | None = None
    from_peer: HasnContactPeerOut | None = None
    message: str = ''


class AgentPeerOut(BaseModel):
    """联系人名下 Agent 摘要"""
    hasn_id: str
    star_id: str
    name: str
    agent_name: str
    avatar: str | None = None
    type: str = 'desktop'
    role: str = 'specialist'
    online_status: str = 'unknown'
    last_seen_at: str | None = None


class HasnContactOut(BaseModel):
    id: int
    peer: HasnContactPeerOut
    relation_type: str
    trust_level: int
    trust_level_label: str = ''
    nickname: str | None = None
    bio: str | None = None
    gender: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    tags: list[str] | None = None
    subscription: bool = False
    status: str = 'connected'
    # 阶段二新增
    owned_agents: list[AgentPeerOut] = []       # human 联系人名下 Agent 列表
    custom_permissions: dict = {}               # 自定义权限覆盖
    scope: dict | None = None                   # 当前作用域
    connected_at: str | None = None
    last_interaction_at: str | None = None
    # Phase 1 US-002: 补齐 contacts 表字段
    interaction_count: int = 0
    request_message: str | None = None
    auto_expire: str | None = None
    peer_owner_id: str | None = None


class HasnContactListResp(BaseModel):
    total: int
    items: list[HasnContactOut]


class HasnTrustLevelReq(BaseModel):
    relation_type: str = Field('social', description='关系类型')
    # 升级为 le=5（原为 le=4），新增 friend(3) / trusted(4) / owner(5)
    trust_level: int = Field(..., ge=0, le=5, description='0-5 (0:blocked~5:owner)')


class HasnPermissionsReq(BaseModel):
    """自定义权限覆盖请求"""
    permissions: dict[str, str] = Field(..., description='action → state 映射 (allow/deny/confirm_required/scope_limited)')
