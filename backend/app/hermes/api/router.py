from fastapi import APIRouter

from backend.core.conf import settings

# --- 管理端（JWT + RBAC） ---
from backend.app.hermes.api.v1.admin.hermes_agent import router as admin_hermes_agent_router
from backend.app.hermes.api.v1.admin.hermes_agent_runtime_state import router as admin_hermes_agent_runtime_state_router
from backend.app.hermes.api.v1.admin.hermes_agent_channel_binding import router as admin_hermes_agent_channel_binding_router
from backend.app.hermes.api.v1.admin.hermes_agent_operation import router as admin_hermes_agent_operation_router
from backend.app.hermes.api.v1.app.agents import router as app_agents_router

# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/hermes/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hermes', tags=['Hermes Agent 管理'])

v1.include_router(admin_hermes_agent_router, prefix='/hermes-agents', tags=['Hermes Agent 管理-Hermes Agent '])
v1.include_router(admin_hermes_agent_runtime_state_router, prefix='/hermes/agent/runtime/states', tags=['Hermes Agent Runtime 状态-Hermes Agent Runtime 状态'])
v1.include_router(admin_hermes_agent_channel_binding_router, prefix='/hermes/agent/channel/bindings', tags=['Hermes Agent 渠道绑定-Hermes Agent 渠道绑定'])
v1.include_router(admin_hermes_agent_operation_router, prefix='/hermes/agent/operations', tags=['Hermes Agent 操作记录-Hermes Agent 操作记录'])




# ========================================
# 用户端 API（JWT）
# 路径前缀: /api/v1/hermes/app
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hermes/app', tags=['Hermes 用户端'])
app.include_router(app_agents_router, prefix='/agents', tags=['Hermes Agent'])
