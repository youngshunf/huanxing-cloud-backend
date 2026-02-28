"""user_tier 路由注册

四层架构（对标 huanxing 模块）:
- admin/  管理端（JWT + RBAC）— 后台管理系统
- app/    用户端（JWT）— 前端用户操作
- open/   公开端（无认证）— 定价页等
- agent/  Agent端（JWT/API Key）— Agent 查询
"""

from fastapi import APIRouter

from backend.core.conf import settings

# --- admin/ 管理端（JWT + RBAC）---
from backend.app.user_tier.api.v1.admin.subscription import router as admin_subscription_router
from backend.app.user_tier.api.v1.admin.credit_balance import router as admin_balance_router
from backend.app.user_tier.api.v1.admin.transaction import router as admin_transaction_router
from backend.app.user_tier.api.v1.admin.package import router as admin_package_router
from backend.app.user_tier.api.v1.admin.tier import router as admin_tier_router
from backend.app.user_tier.api.v1.admin.rate import router as admin_rate_router

# --- app/ 用户端（JWT）---
from backend.app.user_tier.api.v1.app.subscription import router as app_subscription_router

# --- open/ 公开端（无认证）---
from backend.app.user_tier.api.v1.open.pricing import router as open_pricing_router

# --- agent/ Agent端（JWT/API Key）---
from backend.app.user_tier.api.v1.agent.quota import router as agent_quota_router


# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/user_tier/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/user_tier', tags=['订阅积分-管理'])

v1.include_router(admin_subscription_router, prefix='/subscriptions', tags=['管理-用户订阅'])
v1.include_router(admin_balance_router, prefix='/balances', tags=['管理-积分余额'])
v1.include_router(admin_transaction_router, prefix='/transactions', tags=['管理-积分交易'])
v1.include_router(admin_package_router, prefix='/packages', tags=['管理-积分包'])
v1.include_router(admin_tier_router, prefix='/tiers', tags=['管理-订阅等级'])
v1.include_router(admin_rate_router, prefix='/rates', tags=['管理-模型费率'])


# ========================================
# 用户端 API（JWT）
# 路径前缀: /api/v1/user_tier/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/user_tier/app', tags=['订阅积分-用户端'])

app.include_router(app_subscription_router, prefix='/subscription', tags=['用户-订阅管理'])


# ========================================
# 公开 API（无需认证）
# 路径前缀: /api/v1/user_tier/open/
# ========================================
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/user_tier/open', tags=['订阅积分-公开'])

open_api.include_router(open_pricing_router, tags=['公开-定价信息'])


# ========================================
# Agent API（JWT / API Key）
# 路径前缀: /api/v1/user_tier/agent/
# ========================================
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/user_tier/agent', tags=['订阅积分-Agent'])

agent.include_router(agent_quota_router, prefix='/quota', tags=['Agent-配额查询'])
