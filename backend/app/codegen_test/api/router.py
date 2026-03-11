from fastapi import APIRouter

from backend.core.conf import settings

# --- 管理端（JWT + RBAC） ---
from backend.app.codegen_test.api.v1.admin.codegen_test_task import router as admin_codegen_test_task_router
# --- 用户端（仅 JWT） ---
from backend.app.codegen_test.api.v1.app.codegen_test_task import router as app_codegen_test_task_router
# --- Agent（Agent Key） ---
from backend.app.codegen_test.api.v1.agent.codegen_test_task import router as agent_codegen_test_task_router
# --- 公开（无需认证） ---
from backend.app.codegen_test.api.v1.open.codegen_test_task import router as open_codegen_test_task_router

# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/codegen_test/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/codegen_test', tags=['测试任务管理'])

v1.include_router(admin_codegen_test_task_router, prefix='/codegen-test-tasks', tags=['测试任务管理-测试任务'])

# ========================================
# 用户端 API（仅 JWT，无 RBAC）
# 路径前缀: /api/v1/codegen_test/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/codegen_test/app', tags=['测试任务用户端'])

app.include_router(app_codegen_test_task_router, prefix='/codegen-test-tasks', tags=['测试任务用户端-测试任务'])

# ========================================
# 公开 API（无需认证）
# 路径前缀: /api/v1/codegen_test/open/
# ========================================
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/codegen_test/open', tags=['测试任务公开'])

open_api.include_router(open_codegen_test_task_router, tags=['测试任务公开-测试任务'])

# ========================================
# Agent API
# 路径前缀: /api/v1/codegen_test/agent/
# ========================================
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/codegen_test/agent', tags=['测试任务Agent'])

agent.include_router(agent_codegen_test_task_router, prefix='/codegen-test-tasks', tags=['测试任务Agent-测试任务'])
