from fastapi import APIRouter

from backend.core.conf import settings

# --- 管理端（JWT + RBAC） ---
from backend.app.hasn.api.v1.admin.hasn_humans import router as admin_hasn_humans_router
from backend.app.hasn.api.v1.admin.hasn_clients import router as admin_hasn_clients_router
from backend.app.hasn.api.v1.admin.hasn_agents import router as admin_hasn_agents_router
from backend.app.hasn.api.v1.admin.hasn_contacts import router as admin_hasn_contacts_router
from backend.app.hasn.api.v1.admin.hasn_conversations import router as admin_hasn_conversations_router
from backend.app.hasn.api.v1.admin.hasn_messages import router as admin_hasn_messages_router
from backend.app.hasn.api.v1.admin.hasn_unread_counts import router as admin_hasn_unread_counts_router
from backend.app.hasn.api.v1.admin.hasn_group_members import router as admin_hasn_group_members_router
from backend.app.hasn.api.v1.admin.hasn_agent_capabilities import router as admin_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.admin.hasn_trade_sessions import router as admin_hasn_trade_sessions_router
from backend.app.hasn.api.v1.admin.hasn_notifications import router as admin_hasn_notifications_router
from backend.app.hasn.api.v1.admin.hasn_audit_log import router as admin_hasn_audit_log_router

v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN 管理端'])

v1.include_router(admin_hasn_humans_router, prefix='/hasn/humans', tags=['用户管理'])
v1.include_router(admin_hasn_clients_router, prefix='/hasn/clients', tags=['客户端设备'])
v1.include_router(admin_hasn_agents_router, prefix='/hasn/agents', tags=['Agent管理'])
v1.include_router(admin_hasn_contacts_router, prefix='/hasn/contacts', tags=['联系人管理'])
v1.include_router(admin_hasn_conversations_router, prefix='/hasn/conversations', tags=['会话管理'])
v1.include_router(admin_hasn_messages_router, prefix='/hasn/messages', tags=['消息管理'])
v1.include_router(admin_hasn_unread_counts_router, prefix='/hasn/unread/counts', tags=['未读计数'])
v1.include_router(admin_hasn_group_members_router, prefix='/hasn/group/members', tags=['群成员管理'])
v1.include_router(admin_hasn_agent_capabilities_router, prefix='/hasn/agent/capabilities', tags=['Agent能力'])
v1.include_router(admin_hasn_trade_sessions_router, prefix='/hasn/trade/sessions', tags=['交易会话'])
v1.include_router(admin_hasn_notifications_router, prefix='/hasn/notifications', tags=['通知管理'])
v1.include_router(admin_hasn_audit_log_router, prefix='/hasn/audit/logs', tags=['审计日志'])

# --- 用户端（仅 JWT） ---
from backend.app.hasn.api.v1.app.hasn_humans import router as app_hasn_humans_router
from backend.app.hasn.api.v1.app.hasn_clients import router as app_hasn_clients_router
from backend.app.hasn.api.v1.app.hasn_agents import router as app_hasn_agents_router
from backend.app.hasn.api.v1.app.hasn_conversations import router as app_hasn_conversations_router
from backend.app.hasn.api.v1.app.hasn_messages import router as app_hasn_messages_router
from backend.app.hasn.api.v1.app.hasn_unread_counts import router as app_hasn_unread_counts_router
from backend.app.hasn.api.v1.app.hasn_group_members import router as app_hasn_group_members_router
from backend.app.hasn.api.v1.app.hasn_agent_capabilities import router as app_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.app.hasn_trade_sessions import router as app_hasn_trade_sessions_router
from backend.app.hasn.api.v1.app.hasn_notifications import router as app_hasn_notifications_router
from backend.app.hasn.api.v1.app.hasn_audit_log import router as app_hasn_audit_log_router

app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/app', tags=['HASN 用户端'])

app.include_router(app_hasn_humans_router, prefix='/hasn/humans', tags=['用户管理'])
app.include_router(app_hasn_clients_router, prefix='/hasn/clients', tags=['客户端设备'])
app.include_router(app_hasn_agents_router, prefix='/hasn/agents', tags=['Agent管理'])
app.include_router(app_hasn_conversations_router, prefix='/hasn/conversations', tags=['会话管理'])
app.include_router(app_hasn_messages_router, prefix='/hasn/messages', tags=['消息管理'])
app.include_router(app_hasn_unread_counts_router, prefix='/hasn/unread/counts', tags=['未读计数'])
app.include_router(app_hasn_group_members_router, prefix='/hasn/group/members', tags=['群成员管理'])
app.include_router(app_hasn_agent_capabilities_router, prefix='/hasn/agent/capabilities', tags=['Agent能力'])
app.include_router(app_hasn_trade_sessions_router, prefix='/hasn/trade/sessions', tags=['交易会话'])
app.include_router(app_hasn_notifications_router, prefix='/hasn/notifications', tags=['通知管理'])
app.include_router(app_hasn_audit_log_router, prefix='/hasn/audit/logs', tags=['审计日志'])

# --- Agent（Agent Key） ---
from backend.app.hasn.api.v1.agent.hasn_humans import router as agent_hasn_humans_router
from backend.app.hasn.api.v1.agent.hasn_clients import router as agent_hasn_clients_router
from backend.app.hasn.api.v1.agent.hasn_agents import router as agent_hasn_agents_router
from backend.app.hasn.api.v1.agent.hasn_contacts import router as agent_hasn_contacts_router
from backend.app.hasn.api.v1.agent.hasn_conversations import router as agent_hasn_conversations_router
from backend.app.hasn.api.v1.agent.hasn_messages import router as agent_hasn_messages_router
from backend.app.hasn.api.v1.agent.hasn_unread_counts import router as agent_hasn_unread_counts_router
from backend.app.hasn.api.v1.agent.hasn_group_members import router as agent_hasn_group_members_router
from backend.app.hasn.api.v1.agent.hasn_agent_capabilities import router as agent_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.agent.hasn_trade_sessions import router as agent_hasn_trade_sessions_router
from backend.app.hasn.api.v1.agent.hasn_notifications import router as agent_hasn_notifications_router
from backend.app.hasn.api.v1.agent.hasn_audit_log import router as agent_hasn_audit_log_router

agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/agent', tags=['HASN Agent端'])

agent.include_router(agent_hasn_humans_router, prefix='/hasn/humans', tags=['用户管理'])
agent.include_router(agent_hasn_clients_router, prefix='/hasn/clients', tags=['客户端设备'])
agent.include_router(agent_hasn_agents_router, prefix='/hasn/agents', tags=['Agent管理'])
agent.include_router(agent_hasn_contacts_router, prefix='/hasn/contacts', tags=['联系人管理'])
agent.include_router(agent_hasn_conversations_router, prefix='/hasn/conversations', tags=['会话管理'])
agent.include_router(agent_hasn_messages_router, prefix='/hasn/messages', tags=['消息管理'])
agent.include_router(agent_hasn_unread_counts_router, prefix='/hasn/unread/counts', tags=['未读计数'])
agent.include_router(agent_hasn_group_members_router, prefix='/hasn/group/members', tags=['群成员管理'])
agent.include_router(agent_hasn_agent_capabilities_router, prefix='/hasn/agent/capabilities', tags=['Agent能力'])
agent.include_router(agent_hasn_trade_sessions_router, prefix='/hasn/trade/sessions', tags=['交易会话'])
agent.include_router(agent_hasn_notifications_router, prefix='/hasn/notifications', tags=['通知管理'])
agent.include_router(agent_hasn_audit_log_router, prefix='/hasn/audit/logs', tags=['审计日志'])

# --- 公开（无需认证，仅 Agent 能力发现） ---
from backend.app.hasn.api.v1.open.hasn_agent_capabilities import router as open_hasn_agent_capabilities_router

open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/open', tags=['HASN 公开接口'])

open_api.include_router(open_hasn_agent_capabilities_router, prefix='/hasn/agent/capabilities', tags=['Agent能力发现'])

# --- WebSocket 端点（统一节点） ---
from backend.app.hasn.api.ws_node import router as ws_node_router

ws = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN WebSocket'])

ws.include_router(ws_node_router)

# --- 用户端业务 API（联系人 + 认证） ---
from backend.app.hasn.api.v1.app.contacts import router as app_contacts_router
from backend.app.hasn.api.v1.app.hasn_auth_api import router as app_hasn_auth_router
from backend.app.hasn.api.v1.app.hasn_api_keys import router as app_hasn_api_keys_router

app.include_router(app_contacts_router, prefix='/hasn', tags=['联系人管理'])
app.include_router(app_hasn_auth_router, prefix='/hasn', tags=['HASN认证'])
app.include_router(app_hasn_api_keys_router, prefix='/hasn', tags=['HASN API Key'])

