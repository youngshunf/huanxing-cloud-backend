"""HASN 统一路由

合并原 hasn / hasn_core / hasn_social 三个模块的路由，
所有路径统一到 /api/v1/hasn/ 前缀。
"""

from fastapi import APIRouter

from backend.core.conf import settings

# --- HASN 认证 ---
from backend.app.hasn_core.api.v1.hasn_auth_api import router as hasn_auth_api_router

# --- 管理端 ---
from backend.app.hasn_core.api.v1.admin.hasn_humans import router as admin_hasn_humans_router
from backend.app.hasn_core.api.v1.admin.hasn_conversations import router as admin_hasn_conversations_router
from backend.app.hasn_core.api.v1.admin.hasn_messages import router as admin_hasn_messages_router
from backend.app.hasn_core.api.v1.admin.hasn_unread_counts import router as admin_hasn_unread_counts_router
from backend.app.hasn_core.api.v1.admin.hasn_clients import router as admin_hasn_clients_router
from backend.app.hasn_core.api.v1.admin.hasn_agents import router as admin_hasn_agents_router
from backend.app.hasn_core.api.v1.admin.hasn_contacts import router as admin_hasn_contacts_router

# --- 用户端 ---
from backend.app.hasn_core.api.v1.app.hasn_messages import router as app_hasn_messages_router
from backend.app.hasn_core.api.v1.app.hasn_unread_counts import router as app_hasn_unread_counts_router
from backend.app.hasn_core.api.v1.app.hasn_clients import router as app_hasn_clients_router
from backend.app.hasn_core.api.v1.app.hasn_agents import router as app_hasn_agents_router
from backend.app.hasn_core.api.v1.app.contacts import router as contacts_router

# --- Agent ---
from backend.app.hasn_core.api.v1.agent.hasn_messages import router as agent_hasn_messages_router
from backend.app.hasn_core.api.v1.agent.hasn_unread_counts import router as agent_hasn_unread_counts_router

# --- 公开 ---
from backend.app.hasn_core.api.v1.open.hasn_messages import router as open_hasn_messages_router
from backend.app.hasn_core.api.v1.open.hasn_unread_counts import router as open_hasn_unread_counts_router

# --- WebSocket ---
from backend.app.hasn_core.api.ws_client import router as ws_client_router


# ===== 管理端 (JWT + RBAC) =====
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN 管理'])

v1.include_router(admin_hasn_humans_router, prefix='/hasn-humans', tags=['HASN 用户管理'])
v1.include_router(admin_hasn_conversations_router, prefix='/hasn-conversations', tags=['HASN 对话管理'])
v1.include_router(admin_hasn_messages_router, prefix='/hasn-messages', tags=['HASN 消息管理'])
v1.include_router(admin_hasn_unread_counts_router, prefix='/hasn-unread-counts', tags=['HASN 未读计数管理'])
v1.include_router(admin_hasn_clients_router, prefix='/hasn-clients', tags=['HASN 客户端管理'])
v1.include_router(admin_hasn_agents_router, prefix='/hasn-agents', tags=['HASN Agent 管理'])
v1.include_router(admin_hasn_contacts_router, prefix='/hasn-contacts', tags=['HASN 联系人管理'])

# ===== 用户端 (JWT) =====
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/app', tags=['HASN 用户端'])

app.include_router(hasn_auth_api_router, prefix='/hasn', tags=['HASN 认证'])
app.include_router(app_hasn_messages_router, prefix='/hasn-messages', tags=['HASN 消息'])
app.include_router(app_hasn_unread_counts_router, prefix='/hasn-unread-counts', tags=['HASN 未读计数'])
app.include_router(app_hasn_clients_router, prefix='/hasn-clients', tags=['HASN 客户端'])
app.include_router(app_hasn_agents_router, prefix='/hasn-agents', tags=['HASN Agent'])
app.include_router(contacts_router, tags=['HASN 联系人'])

# ===== Agent (API Key) =====
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/agent', tags=['HASN Agent API'])

agent.include_router(agent_hasn_messages_router, prefix='/hasn-messages', tags=['HASN 消息'])
agent.include_router(agent_hasn_unread_counts_router, prefix='/hasn-unread-counts', tags=['HASN 未读计数'])

# ===== 公开 =====
open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/open', tags=['HASN 公开'])

open_api.include_router(open_hasn_messages_router, prefix='/hasn-messages', tags=['HASN 消息'])
open_api.include_router(open_hasn_unread_counts_router, prefix='/hasn-unread-counts', tags=['HASN 未读计数'])

# ===== WebSocket =====
ws = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN WebSocket'])
ws.include_router(ws_client_router)
