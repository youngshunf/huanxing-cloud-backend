from fastapi import APIRouter

from backend.core.conf import settings

# --- 管理端（JWT + RBAC） ---
from backend.app.hasn.api.v1.admin.hasn_clients import router as admin_hasn_clients_router
from backend.app.hasn.api.v1.admin.hasn_agents import router as admin_hasn_agents_router
# --- 用户端（仅 JWT） ---
from backend.app.hasn.api.v1.app.hasn_clients import router as app_hasn_clients_router
from backend.app.hasn.api.v1.app.hasn_agents import router as app_hasn_agents_router

# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/hasn/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN 客户端设备管理'])

v1.include_router(admin_hasn_clients_router, prefix='/hasn-clientss', tags=['HASN 客户端设备管理-HASN 客户端设备'])
v1.include_router(admin_hasn_agents_router, prefix='/hasn-agentss', tags=['HASN Agent -HASN Agent '])

# ========================================
# 用户端 API（仅 JWT，无 RBAC）
# 路径前缀: /api/v1/hasn/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/app', tags=['HASN 客户端设备用户端'])

app.include_router(app_hasn_clients_router, prefix='/hasn-clientss', tags=['HASN 客户端设备用户端-HASN 客户端设备'])


