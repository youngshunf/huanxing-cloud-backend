from fastapi import APIRouter

from backend.core.conf import settings

# --- 集成 API（用户端） ---
from backend.app.integration.api.integration_api import router as integration_router
# --- 管理端（JWT + RBAC） ---
from backend.app.integration.api.v1.admin.integration_apps import router as admin_integration_apps_router
from backend.app.integration.api.v1.admin.integration_credentials import router as admin_integration_credentials_router
# --- 用户端（仅 JWT） ---
from backend.app.integration.api.v1.app.integration_apps import router as app_integration_apps_router
from backend.app.integration.api.v1.app.integration_credentials import router as app_integration_credentials_router
# --- Agent（Agent Key） ---
from backend.app.integration.api.v1.agent.integration_apps import router as agent_integration_apps_router
from backend.app.integration.api.v1.agent.integration_credentials import router as agent_integration_credentials_router
# --- 公开（无需认证） ---
from backend.app.integration.api.v1.open.integration_apps import router as open_integration_apps_router
from backend.app.integration.api.v1.open.integration_credentials import router as open_integration_credentials_router

# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/integration/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/integration', tags=['第三方应用集成配置管理'])

v1.include_router(admin_integration_apps_router, prefix='/integration-apps', tags=['第三方应用集成配置管理-第三方应用集成配置'])
v1.include_router(admin_integration_credentials_router, prefix='/integration/credentialss', tags=['用户第三方应用凭证-用户第三方应用凭证'])

# ========================================
# 用户端 API（仅 JWT，无 RBAC）
# 路径前缀: /api/v1/integration/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/integration/app', tags=['第三方应用集成配置用户端'])

# 集成 API（连接、断开、获取状态等）
app.include_router(integration_router, tags=['第三方应用集成'])
app.include_router(app_integration_apps_router, prefix='/integration-apps', tags=['第三方应用集成配置用户端-第三方应用集成配置'])
app.include_router(app_integration_credentials_router, prefix='/integration/credentialss', tags=['用户第三方应用凭证-用户第三方应用凭证'])

# ========================================
# 公开 API（无需认证）
# 路径前缀: /api/v1/integration/open/
# ========================================
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/integration/open', tags=['第三方应用集成配置公开'])

open_api.include_router(open_integration_apps_router, prefix='/integration-apps', tags=['第三方应用集成配置公开-第三方应用集成配置'])
open_api.include_router(open_integration_credentials_router, prefix='/integration/credentialss', tags=['用户第三方应用凭证-用户第三方应用凭证'])

# ========================================
# Agent API
# 路径前缀: /api/v1/integration/agent/
# ========================================
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/integration/agent', tags=['第三方应用集成配置Agent'])

agent.include_router(agent_integration_apps_router, prefix='/integration-apps', tags=['第三方应用集成配置Agent-第三方应用集成配置'])
agent.include_router(agent_integration_credentials_router, prefix='/integration/credentialss', tags=['用户第三方应用凭证-用户第三方应用凭证'])
