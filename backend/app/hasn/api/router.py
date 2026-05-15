from fastapi import APIRouter

from backend.core.conf import settings

# --- 管理端（JWT + RBAC） ---
from backend.app.hasn.api.v1.onboarding import router as onboarding_router
from backend.app.hasn.api.v1.message_hub import router as message_hub_router
from backend.app.hasn.api.v1.sync import router as sync_router
from backend.app.hasn.api.v1.admin.hasn_humans import router as admin_hasn_humans_router
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
from backend.app.hasn.api.v1.admin.hasn_nodes import router as admin_hasn_nodes_router
from backend.app.hasn.api.v1.admin.hasn_owner_api_keys import router as admin_hasn_owner_api_keys_router
from backend.app.hasn.api.v1.admin.hasn_node_bindings import router as admin_hasn_node_bindings_router
from backend.app.hasn.api.v1.admin.hasn_agent_runtime_reports import router as admin_hasn_agent_runtime_reports_router
from backend.app.hasn.api.v1.admin.hasn_channel_bindings import router as admin_hasn_channel_bindings_router
from backend.app.hasn.api.v1.admin.hasn_clients import router as admin_hasn_clients_router
from backend.app.hasn.api.v1.admin.hasn_pending_intents import router as admin_hasn_pending_intents_router
from backend.app.hasn.api.v1.admin.hasn_suppressed_messages import router as admin_hasn_suppressed_messages_router
from backend.app.hasn.api.v1.admin.hasn_sync_events import router as admin_hasn_sync_events_router
from backend.app.hasn.api.v1.admin.hasn_sync_inbox_events import router as admin_hasn_sync_inbox_events_router
from backend.app.hasn.api.v1.admin.hasn_tenant_sandboxes import router as admin_hasn_tenant_sandboxes_router

v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN 管理端'])

v1.include_router(onboarding_router, tags=['HASN Onboarding'])
v1.include_router(message_hub_router, tags=['HASN MessageHub'])
v1.include_router(sync_router, tags=['HASN Sync'])
v1.include_router(admin_hasn_humans_router, prefix='/humans', tags=['用户管理'])
v1.include_router(admin_hasn_agents_router, prefix='/agents', tags=['Agent管理'])
v1.include_router(admin_hasn_contacts_router, prefix='/contacts', tags=['联系人管理'])
v1.include_router(admin_hasn_conversations_router, prefix='/conversations', tags=['会话管理'])
v1.include_router(admin_hasn_messages_router, prefix='/messages', tags=['消息管理'])
v1.include_router(admin_hasn_unread_counts_router, prefix='/unread/counts', tags=['未读计数'])
v1.include_router(admin_hasn_group_members_router, prefix='/group/members', tags=['群成员管理'])
v1.include_router(admin_hasn_agent_capabilities_router, prefix='/agent/capabilities', tags=['Agent能力'])
v1.include_router(admin_hasn_trade_sessions_router, prefix='/trade/sessions', tags=['交易会话'])
v1.include_router(admin_hasn_notifications_router, prefix='/notifications', tags=['通知管理'])
v1.include_router(admin_hasn_audit_log_router, prefix='/audit/logs', tags=['审计日志'])
v1.include_router(admin_hasn_nodes_router, prefix='/hasn/nodess', tags=['HASN Node 主-HASN Node 主'])
v1.include_router(admin_hasn_owner_api_keys_router, prefix='/hasn/owner/api/keyss', tags=['HASN Owner API Key -HASN Owner API Key '])
v1.include_router(admin_hasn_node_bindings_router, prefix='/hasn/node/bindingss', tags=['HASN Node Owner Binding 租约-HASN Node Owner Binding 租约'])
v1.include_router(admin_hasn_agent_runtime_reports_router, prefix='/runtime/reports', tags=['HASN Runtime reports'])
v1.include_router(admin_hasn_channel_bindings_router, prefix='/channel/bindings', tags=['HASN Channel bindings'])
v1.include_router(admin_hasn_clients_router, prefix='/clients', tags=['HASN Clients'])
v1.include_router(admin_hasn_pending_intents_router, prefix='/pending/intents', tags=['HASN Pending intents'])
v1.include_router(admin_hasn_suppressed_messages_router, prefix='/suppressed/messages', tags=['HASN Suppressed messages'])
v1.include_router(admin_hasn_sync_events_router, prefix='/sync/events', tags=['HASN Sync events'])
v1.include_router(admin_hasn_sync_inbox_events_router, prefix='/sync/inbox/events', tags=['HASN Sync inbox events'])
v1.include_router(admin_hasn_tenant_sandboxes_router, prefix='/tenant/sandboxes', tags=['HASN Tenant sandboxes'])

# --- 用户端（仅 JWT） ---
from backend.app.hasn.api.v1.app.hasn_humans import router as app_hasn_humans_router
from backend.app.hasn.api.v1.app.hasn_agents import router as app_hasn_agents_router
from backend.app.hasn.api.v1.app.hasn_conversations import router as app_hasn_conversations_router
from backend.app.hasn.api.v1.app.hasn_messages import router as app_hasn_messages_router
from backend.app.hasn.api.v1.app.hasn_unread_counts import router as app_hasn_unread_counts_router
from backend.app.hasn.api.v1.app.hasn_group_members import router as app_hasn_group_members_router
from backend.app.hasn.api.v1.app.hasn_agent_capabilities import router as app_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.app.hasn_trade_sessions import router as app_hasn_trade_sessions_router
from backend.app.hasn.api.v1.app.hasn_notifications import router as app_hasn_notifications_router
from backend.app.hasn.api.v1.app.hasn_audit_log import router as app_hasn_audit_log_router
from backend.app.hasn.api.agent_scopes import router as agent_scopes_router

app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/app', tags=['HASN 用户端'])

app.include_router(app_hasn_humans_router, prefix='/humans', tags=['用户管理'])
app.include_router(app_hasn_agents_router, prefix='/agents', tags=['Agent管理'])
app.include_router(app_hasn_conversations_router, prefix='/conversations', tags=['会话管理'])
app.include_router(app_hasn_messages_router, prefix='/messages', tags=['消息管理'])
app.include_router(app_hasn_unread_counts_router, prefix='/unread/counts', tags=['未读计数'])
app.include_router(app_hasn_group_members_router, prefix='/group/members', tags=['群成员管理'])
app.include_router(app_hasn_agent_capabilities_router, prefix='/agent/capabilities', tags=['Agent能力'])
app.include_router(app_hasn_trade_sessions_router, prefix='/trade/sessions', tags=['交易会话'])
app.include_router(app_hasn_notifications_router, prefix='/notifications', tags=['通知管理'])
app.include_router(app_hasn_audit_log_router, prefix='/audit/logs', tags=['审计日志'])
app.include_router(agent_scopes_router, tags=['Agent权限管理'])

# --- Agent（Agent Key） ---
from backend.app.hasn.api.v1.agent.hasn_humans import router as agent_hasn_humans_router
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
from backend.app.hasn.api.v1.agent.hasn_nodes import router as agent_hasn_nodes_router

agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/agent', tags=['HASN Agent端'])

agent.include_router(agent_hasn_humans_router, prefix='/humans', tags=['用户管理'])
agent.include_router(agent_hasn_agents_router, prefix='/agents', tags=['Agent管理'])
agent.include_router(agent_hasn_contacts_router, prefix='/contacts', tags=['联系人管理'])
agent.include_router(agent_hasn_conversations_router, prefix='/conversations', tags=['会话管理'])
agent.include_router(agent_hasn_messages_router, prefix='/messages', tags=['消息管理'])
agent.include_router(agent_hasn_unread_counts_router, prefix='/unread/counts', tags=['未读计数'])
agent.include_router(agent_hasn_group_members_router, prefix='/group/members', tags=['群成员管理'])
agent.include_router(agent_hasn_agent_capabilities_router, prefix='/agent/capabilities', tags=['Agent能力'])
agent.include_router(agent_hasn_trade_sessions_router, prefix='/trade/sessions', tags=['交易会话'])
agent.include_router(agent_hasn_notifications_router, prefix='/notifications', tags=['通知管理'])
agent.include_router(agent_hasn_audit_log_router, prefix='/audit/logs', tags=['审计日志'])
agent.include_router(agent_hasn_nodes_router, prefix='/hasn/nodess', tags=['HASN Node 主-HASN Node 主'])

# --- 公开（无需认证，仅 Agent 能力发现） ---
from backend.app.hasn.api.v1.open.hasn_agent_capabilities import router as open_hasn_agent_capabilities_router

open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/open', tags=['HASN 公开接口'])

open_api.include_router(open_hasn_agent_capabilities_router, prefix='/agent/capabilities', tags=['Agent能力发现'])
# open_hasn_nodes_router 已移除（v2.1: 节点注册在 WS 建连时自动完成）

# --- WebSocket 端点（统一节点） ---
from backend.app.hasn.api.ws_node import router as ws_node_router

ws = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN WebSocket'])

ws.include_router(ws_node_router)

# --- 用户端业务 API（联系人 + 认证 + 搜索） ---
from backend.app.hasn.api.v1.app.contacts import router as app_contacts_router
from backend.app.hasn.api.v1.app.hasn_auth_api import router as app_hasn_auth_router
from backend.app.hasn.api.v1.app.hasn_api_keys import router as app_hasn_api_keys_router
from backend.app.hasn.api.v1.app.hasn_nodes import router as app_hasn_nodes_router
from backend.app.hasn.api.v1.app.hasn_owner_api_keys import router as app_hasn_owner_api_keys_router
from backend.app.hasn.api.v1.app.search import router as app_users_search_router
from backend.app.hasn.api.v1.app.profile import router as app_profile_router
from backend.app.hasn.api.v1.node_control import router as node_control_router

app.include_router(app_contacts_router, tags=['联系人管理'])
app.include_router(app_hasn_auth_router, tags=['HASN认证'])
app.include_router(app_users_search_router, tags=['HASN Users'])
app.include_router(app_profile_router, prefix='/profile', tags=['合并 Profile (sys_user + hasn_humans)'])

# --- IM 业务 API ---
from backend.app.hasn.api.v1.app.hasn_im import router as app_hasn_im_router
app.include_router(app_hasn_im_router, prefix='/im', tags=['HASN IM 业务'])
app.include_router(app_hasn_api_keys_router, tags=['HASN API Key'])
app.include_router(app_hasn_nodes_router, prefix='/hasn/nodess', tags=['HASN Node 主-HASN Node 主'])
app.include_router(app_hasn_owner_api_keys_router, prefix='/hasn/owner/api/keyss', tags=['HASN Owner API Key -HASN Owner API Key '])
v1.include_router(node_control_router, tags=['HASN Node 控制平面'])
