from fastapi import APIRouter

from backend.core.conf import settings

# --- admin/ 管理端（JWT + RBAC）---
from backend.app.huanxing.api.v1.admin.server import router as admin_server_router
from backend.app.huanxing.api.v1.admin.user import router as admin_user_router
from backend.app.huanxing.api.v1.admin.document import router as admin_document_router
from backend.app.huanxing.api.v1.admin.document_version import router as admin_doc_version_router
from backend.app.huanxing.api.v1.admin.document_autosave import router as admin_doc_autosave_router
from backend.app.huanxing.api.v1.admin.document_folder import router as admin_doc_folder_router
from backend.app.huanxing.api.v1.admin.dashboard import router as admin_dashboard_router
from backend.app.huanxing.api.v1.admin.analytics import router as admin_analytics_router

# --- app/ 用户端（仅 JWT）---
from backend.app.huanxing.api.v1.app.document import router as app_document_router
from backend.app.huanxing.api.v1.app.folder import router as app_folder_router

# --- open/ 公开（无需认证）---
from backend.app.huanxing.api.v1.open.share import router as open_share_router

# --- agent/ Agent ---
from backend.app.huanxing.api.v1.agent.document import router as agent_document_router
from backend.app.huanxing.api.v1.agent.user_sync import router as agent_user_sync_router


# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/huanxing/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/huanxing', tags=['唤星管理'])

v1.include_router(admin_server_router, prefix='/servers', tags=['唤星管理-服务器'])
v1.include_router(admin_user_router, prefix='/users', tags=['唤星管理-用户'])
v1.include_router(admin_document_router, prefix='/documents', tags=['唤星管理-文档'])
v1.include_router(admin_doc_version_router, prefix='/document/versions', tags=['唤星管理-文档版本'])
v1.include_router(admin_doc_autosave_router, prefix='/document/autosaves', tags=['唤星管理-自动保存'])
v1.include_router(admin_doc_folder_router, prefix='/document-folders', tags=['唤星管理-文档目录'])
v1.include_router(admin_dashboard_router, prefix='/dashboard', tags=['唤星管理-数据看板'])
v1.include_router(admin_analytics_router, prefix='/analytics', tags=['唤星管理-分析看板'])

# ========================================
# 用户端 API（仅 JWT，无 RBAC）
# 路径前缀: /api/v1/huanxing/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/huanxing/app', tags=['唤星用户端'])

app.include_router(app_document_router, prefix='/docs', tags=['唤星用户端-文档'])
app.include_router(app_folder_router, prefix='/folders', tags=['唤星用户端-目录'])

# ========================================
# 公开 API（无需认证）
# 路径前缀: /api/v1/huanxing/open/
# ========================================
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/huanxing/open', tags=['唤星公开'])

open_api.include_router(open_share_router, tags=['唤星公开-分享'])

# ========================================
# Agent API
# 路径前缀: /api/v1/huanxing/agent/
# ========================================
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/huanxing/agent', tags=['唤星Agent'])

agent.include_router(agent_document_router, prefix='/docs', tags=['唤星Agent-文档'])
agent.include_router(agent_user_sync_router, prefix='/users', tags=['唤星Agent-用户同步'])
