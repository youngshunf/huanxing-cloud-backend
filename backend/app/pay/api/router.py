"""pay 模块路由注册

三层架构:
- v1/      管理端（JWT + RBAC）— 后台管理系统
- app/     用户端（JWT）— 前端用户操作
- open/    公开端（无认证）— 支付回调
"""

from fastapi import APIRouter

from backend.core.conf import settings

# --- admin/ 管理端（JWT + RBAC）---
from backend.app.pay.api.v1.admin.merchant import router as admin_merchant_router
from backend.app.pay.api.v1.admin.channel import router as admin_channel_router
from backend.app.pay.api.v1.admin.order import router as admin_order_router
from backend.app.pay.api.v1.admin.contract import router as admin_contract_router
from backend.app.pay.api.v1.admin.notify_log import router as admin_notify_log_router

# --- app/ 用户端（JWT）---
from backend.app.pay.api.v1.app.pay import router as app_pay_router

# --- open/ 公开端（无认证）---
from backend.app.pay.api.v1.open.notify import router as open_notify_router


# ========================================
# 管理端 API（JWT + RBAC）
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/pay', tags=['支付管理'])

v1.include_router(admin_merchant_router, prefix='/merchants', tags=['支付管理-商户'])
v1.include_router(admin_channel_router, prefix='/channels', tags=['支付管理-渠道'])
v1.include_router(admin_order_router, prefix='/orders', tags=['支付管理-订单'])
v1.include_router(admin_contract_router, prefix='/contracts', tags=['支付管理-签约'])
v1.include_router(admin_notify_log_router, prefix='/notify-logs', tags=['支付管理-回调日志'])


# ========================================
# 用户端 API（JWT）
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/pay/app', tags=['支付-用户端'])

app.include_router(app_pay_router, tags=['支付-用户端'])


# ========================================
# 公开 API（无需认证）
# ========================================
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/pay/open', tags=['支付-公开'])

open_api.include_router(open_notify_router, tags=['支付-回调'])
