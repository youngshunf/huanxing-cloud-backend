"""
HASN Schema 定义 — 身份 & 认证
对应设计文档: 01-身份体系.md / 07-API设计.md
"""
from pydantic import BaseModel, Field


# ══════════════════════════════════════
# 注册
# ══════════════════════════════════════

class HasnRegisterReq(BaseModel):
    """内部注册接口 (Guardian 调用)"""
    phone: str | None = Field(None, description='手机号')
    huanxing_user_id: str = Field(..., description='唤星平台 user_id')
    nickname: str = Field(..., max_length=100, description='昵称')
    agent_name: str = Field('星灵', max_length=50, description='默认 Agent 名')


class HasnHumanOut(BaseModel):
    hasn_id: str = Field(..., description='h_uuid')
    star_id: str = Field(..., description='唤星号')
    name: str
    jwt_token: str | None = None
    refresh_token: str | None = None


class HasnAgentOut(BaseModel):
    hasn_id: str = Field(..., description='a_uuid')
    star_id: str = Field(..., description='100001#star')
    name: str
    api_key: str | None = Field(None, description='仅注册时返回明文，之后不可查')


class HasnRegisterResp(BaseModel):
    human: HasnHumanOut
    agent: HasnAgentOut


# ══════════════════════════════════════
# 登录 / Token
# ══════════════════════════════════════

class HasnLoginReq(BaseModel):
    phone: str = Field(..., description='手机号')
    sms_code: str = Field(..., description='短信验证码')


class HasnTokenResp(BaseModel):
    hasn_id: str
    star_id: str
    jwt_token: str
    refresh_token: str | None = None
    expires_in: int = 86400


# ══════════════════════════════════════
# Profile
# ══════════════════════════════════════

class HasnProfileUpdateReq(BaseModel):
    name: str | None = Field(None, max_length=100)
    bio: str | None = None
    avatar_url: str | None = None
    tags: list[str] | None = None
    contact_policy: dict | None = None


class HasnProfileOut(BaseModel):
    hasn_id: str
    star_id: str
    type: str  # human / agent
    name: str
    bio: str = ''
    avatar_url: str | None = None
    status: str = 'active'
    agents_count: int | None = None  # 仅 human


# ══════════════════════════════════════
# 搜索
# ══════════════════════════════════════

class HasnSearchResultItem(BaseModel):
    star_id: str
    name: str
    type: str  # human / agent
    avatar_url: str | None = None
    bio: str = ''
    agents_count: int | None = None
    contact_status: str = 'none'  # none/pending/connected


class HasnSearchResp(BaseModel):
    total: int
    items: list[HasnSearchResultItem]
