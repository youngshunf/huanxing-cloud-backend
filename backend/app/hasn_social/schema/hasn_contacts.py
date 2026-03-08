"""
HASN Schema 定义 — 联系人 & 好友请求
对应设计文档: 07-API设计.md §三
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ══════════════════════════════════════
# 联系人 (基础)
# ══════════════════════════════════════

class HasnContactPeerOut(BaseModel):
    hasn_id: str
    star_id: str
    name: str
    type: str  # human / agent
    avatar_url: str | None = None
    status: str = 'active'


# ══════════════════════════════════════
# 好友请求
# ══════════════════════════════════════

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
    relation_type: str = 'social'
    target: HasnContactPeerOut | None = None
    from_peer: HasnContactPeerOut | None = None
    message: str = ''


# ══════════════════════════════════════
# 联系人列表
# ══════════════════════════════════════

TRUST_LEVEL_LABELS = {0: 'blocked', 1: 'stranger', 2: 'normal', 3: 'trusted', 4: 'owner'}


class HasnContactOut(BaseModel):
    id: int
    peer: HasnContactPeerOut
    relation_type: str
    trust_level: int
    trust_level_label: str = ''
    nickname: str | None = None
    tags: list[str] | None = None
    subscription: bool = False
    status: str = 'connected'
    connected_at: str | None = None
    last_interaction_at: str | None = None


class HasnContactListResp(BaseModel):
    total: int
    items: list[HasnContactOut]


# ══════════════════════════════════════
# 信任等级
# ══════════════════════════════════════

class HasnTrustLevelReq(BaseModel):
    relation_type: str = Field('social', description='关系类型')
    trust_level: int = Field(..., ge=0, le=4, description='0-4')
