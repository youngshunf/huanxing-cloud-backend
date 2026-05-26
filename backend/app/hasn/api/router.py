from fastapi import APIRouter

from backend.app.hasn.api.v1.admin.hasn_agent_capabilities import router as admin_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.admin.hasn_agent_runtime_reports import router as admin_hasn_agent_runtime_reports_router
from backend.app.hasn.api.v1.admin.hasn_agents import router as admin_hasn_agents_router
from backend.app.hasn.api.v1.admin.hasn_audit_log import router as admin_hasn_audit_log_router
from backend.app.hasn.api.v1.admin.hasn_channel_bindings import router as admin_hasn_channel_bindings_router
from backend.app.hasn.api.v1.admin.hasn_clients import router as admin_hasn_clients_router
from backend.app.hasn.api.v1.admin.hasn_contacts import router as admin_hasn_contacts_router
from backend.app.hasn.api.v1.admin.hasn_conversations import router as admin_hasn_conversations_router
from backend.app.hasn.api.v1.admin.hasn_enterprise import router as admin_hasn_enterprise_router
from backend.app.hasn.api.v1.admin.hasn_enterprise_invite_code import router as admin_hasn_enterprise_invite_code_router
from backend.app.hasn.api.v1.admin.hasn_enterprise_membership import router as admin_hasn_enterprise_membership_router
from backend.app.hasn.api.v1.admin.hasn_group_members import router as admin_hasn_group_members_router
from backend.app.hasn.api.v1.admin.hasn_humans import router as admin_hasn_humans_router
from backend.app.hasn.api.v1.admin.hasn_messages import router as admin_hasn_messages_router
from backend.app.hasn.api.v1.admin.hasn_node_bindings import router as admin_hasn_node_bindings_router
from backend.app.hasn.api.v1.admin.hasn_nodes import router as admin_hasn_nodes_router
from backend.app.hasn.api.v1.admin.hasn_notifications import router as admin_hasn_notifications_router
from backend.app.hasn.api.v1.admin.hasn_owner_api_keys import router as admin_hasn_owner_api_keys_router
from backend.app.hasn.api.v1.admin.hasn_pending_intents import router as admin_hasn_pending_intents_router
from backend.app.hasn.api.v1.admin.hasn_ragflow_credential import router as admin_hasn_ragflow_credential_router
from backend.app.hasn.api.v1.admin.hasn_ragflow_instance import router as admin_hasn_ragflow_instance_router
from backend.app.hasn.api.v1.admin.hasn_suppressed_messages import router as admin_hasn_suppressed_messages_router
from backend.app.hasn.api.v1.admin.hasn_sync_events import router as admin_hasn_sync_events_router
from backend.app.hasn.api.v1.admin.hasn_sync_inbox_events import router as admin_hasn_sync_inbox_events_router
from backend.app.hasn.api.v1.admin.hasn_tenant_sandboxes import router as admin_hasn_tenant_sandboxes_router
from backend.app.hasn.api.v1.admin.hasn_trade_sessions import router as admin_hasn_trade_sessions_router
from backend.app.hasn.api.v1.admin.hasn_unread_counts import router as admin_hasn_unread_counts_router
from backend.app.hasn.api.v1.admin.hasn_user_active_workspace import router as admin_hasn_user_active_workspace_router
from backend.app.hasn.api.v1.admin.hasn_workspace_app import router as admin_hasn_workspace_app_router
from backend.app.hasn.api.v1.admin.hasn_posts import router as admin_hasn_posts_router
from backend.app.hasn.api.v1.admin.hasn_articles import router as admin_hasn_articles_router
from backend.app.hasn.api.v1.admin.hasn_comments import router as admin_hasn_comments_router
from backend.app.hasn.api.v1.admin.hasn_follows import router as admin_hasn_follows_router
from backend.app.hasn.api.v1.admin.hasn_likes import router as admin_hasn_likes_router
from backend.app.hasn.api.v1.admin.hasn_collections import router as admin_hasn_collections_router
from backend.app.hasn.api.v1.admin.hasn_collection_items import router as admin_hasn_collection_items_router
from backend.app.hasn.api.v1.admin.hasn_skill_bundle import router as admin_hasn_skill_bundle_router
from backend.app.hasn.api.v1.admin.hasn_task import router as admin_hasn_task_router
from backend.app.hasn.api.v1.admin.hasn_task_run import router as admin_hasn_task_run_router
from backend.app.hasn.api.v1.admin.hasn_sessions import router as admin_hasn_sessions_router
from backend.app.hasn.api.v1.admin.hasn_session_events import router as admin_hasn_session_events_router
from backend.app.hasn.api.v1.admin.hasn_session_artifacts import router as admin_hasn_session_artifacts_router
from backend.app.hasn.api.v1.ai_native_app import audit_router as ai_native_audit_router
from backend.app.hasn.api.v1.ai_native_app import apps_router as ai_native_apps_router
from backend.app.hasn.api.v1.ai_native_app import runtime_router as ai_native_runtime_router
from backend.app.hasn.api.v1.message_hub import router as message_hub_router

# --- 管理端（JWT + RBAC） ---
from backend.app.hasn.api.v1.onboarding import router as onboarding_router
from backend.app.hasn.api.v1.sync import router as sync_router
from backend.core.conf import settings

ai_native = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/ai-native', tags=['AI-Native 应用平台'])
ai_native.include_router(ai_native_apps_router, prefix='/apps', tags=['AI-Native 应用平台-应用'])
ai_native.include_router(ai_native_runtime_router, prefix='/runtime', tags=['AI-Native 应用平台-运行时'])
ai_native.include_router(ai_native_audit_router, prefix='/audit', tags=['AI-Native 应用平台-审计'])

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
v1.include_router(
    admin_hasn_owner_api_keys_router, prefix='/hasn/owner/api/keyss', tags=['HASN Owner API Key -HASN Owner API Key ']
)
v1.include_router(
    admin_hasn_node_bindings_router,
    prefix='/hasn/node/bindingss',
    tags=['HASN Node Owner Binding 租约-HASN Node Owner Binding 租约'],
)
v1.include_router(admin_hasn_agent_runtime_reports_router, prefix='/runtime/reports', tags=['HASN Runtime reports'])
v1.include_router(admin_hasn_channel_bindings_router, prefix='/channel/bindings', tags=['HASN Channel bindings'])
v1.include_router(admin_hasn_clients_router, prefix='/clients', tags=['HASN Clients'])
v1.include_router(admin_hasn_pending_intents_router, prefix='/pending/intents', tags=['HASN Pending intents'])
v1.include_router(
    admin_hasn_suppressed_messages_router, prefix='/suppressed/messages', tags=['HASN Suppressed messages']
)
v1.include_router(admin_hasn_sync_events_router, prefix='/sync/events', tags=['HASN Sync events'])
v1.include_router(admin_hasn_sync_inbox_events_router, prefix='/sync/inbox/events', tags=['HASN Sync inbox events'])
v1.include_router(admin_hasn_tenant_sandboxes_router, prefix='/tenant/sandboxes', tags=['HASN Tenant sandboxes'])
v1.include_router(admin_hasn_enterprise_router, prefix='/enterprises', tags=['企业管理'])
v1.include_router(admin_hasn_enterprise_membership_router, prefix='/enterprise/memberships', tags=['企业成员关系'])
v1.include_router(admin_hasn_enterprise_invite_code_router, prefix='/enterprise/invite-codes', tags=['企业邀请码'])
v1.include_router(admin_hasn_user_active_workspace_router, prefix='/user/active-workspaces', tags=['活跃工作区'])
v1.include_router(admin_hasn_workspace_app_router, prefix='/workspace/apps', tags=['工作空间应用'])
v1.include_router(admin_hasn_ragflow_instance_router, prefix='/ragflow/instances', tags=['RAGFlow 实例'])
v1.include_router(admin_hasn_ragflow_credential_router, prefix='/ragflow/credentials', tags=['RAGFlow 凭据'])

# --- 用户端（仅 JWT） ---
from backend.app.hasn.api.agent_scopes import router as agent_scopes_router
from backend.app.hasn.api.v1.app.hasn_agent_capabilities import router as app_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.app.hasn_agents import router as app_hasn_agents_router
from backend.app.hasn.api.v1.app.hasn_audit_log import router as app_hasn_audit_log_router
from backend.app.hasn.api.v1.app.hasn_conversations import router as app_hasn_conversations_router
from backend.app.hasn.api.v1.app.hasn_group_members import router as app_hasn_group_members_router
from backend.app.hasn.api.v1.app.hasn_humans import router as app_hasn_humans_router
from backend.app.hasn.api.v1.app.hasn_messages import router as app_hasn_messages_router
from backend.app.hasn.api.v1.app.hasn_notifications import router as app_hasn_notifications_router
from backend.app.hasn.api.v1.app.hasn_trade_sessions import router as app_hasn_trade_sessions_router
from backend.app.hasn.api.v1.app.hasn_unread_counts import router as app_hasn_unread_counts_router
from backend.app.hasn.api.v1.app.knowledge import router as app_knowledge_router

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
app.include_router(app_knowledge_router, tags=['知识库'])
app.include_router(agent_scopes_router, tags=['Agent权限管理'])

# --- Agent（Agent Key） ---
from backend.app.hasn.api.v1.agent.hasn_agent_capabilities import router as agent_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.agent.hasn_agents import router as agent_hasn_agents_router
from backend.app.hasn.api.v1.agent.hasn_audit_log import router as agent_hasn_audit_log_router
from backend.app.hasn.api.v1.agent.hasn_contacts import router as agent_hasn_contacts_router
from backend.app.hasn.api.v1.agent.hasn_conversations import router as agent_hasn_conversations_router
from backend.app.hasn.api.v1.agent.hasn_group_members import router as agent_hasn_group_members_router
from backend.app.hasn.api.v1.agent.hasn_humans import router as agent_hasn_humans_router
from backend.app.hasn.api.v1.agent.hasn_messages import router as agent_hasn_messages_router
from backend.app.hasn.api.v1.agent.hasn_nodes import router as agent_hasn_nodes_router
from backend.app.hasn.api.v1.agent.hasn_notifications import router as agent_hasn_notifications_router
from backend.app.hasn.api.v1.agent.hasn_trade_sessions import router as agent_hasn_trade_sessions_router
from backend.app.hasn.api.v1.agent.hasn_unread_counts import router as agent_hasn_unread_counts_router
from backend.app.hasn.api.v1.agent.hasn_posts import router as agent_hasn_posts_router
from backend.app.hasn.api.v1.agent.hasn_articles import router as agent_hasn_articles_router
from backend.app.hasn.api.v1.agent.hasn_comments import router as agent_hasn_comments_router
from backend.app.hasn.api.v1.agent.hasn_follows import router as agent_hasn_follows_router
from backend.app.hasn.api.v1.agent.hasn_likes import router as agent_hasn_likes_router
from backend.app.hasn.api.v1.agent.hasn_collections import router as agent_hasn_collections_router
from backend.app.hasn.api.v1.agent.hasn_collection_items import router as agent_hasn_collection_items_router
from backend.app.hasn.api.v1.agent.hasn_skill_bundle import router as agent_hasn_skill_bundle_router
from backend.app.hasn.api.v1.agent.hasn_task import router as agent_hasn_task_router
from backend.app.hasn.api.v1.agent.hasn_task_run import router as agent_hasn_task_run_router
from backend.app.hasn.api.v1.agent.hasn_sessions import router as agent_hasn_sessions_router
from backend.app.hasn.api.v1.agent.hasn_session_events import router as agent_hasn_session_events_router
from backend.app.hasn.api.v1.agent.hasn_session_artifacts import router as agent_hasn_session_artifacts_router

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
# 注释掉 codegen 生成的社区表 agent 路由
# agent.include_router(agent_hasn_posts_router, prefix='/hasn/postss', tags=['社区帖子-社区帖子'])
# agent.include_router(agent_hasn_articles_router, prefix='/hasn/articless', tags=['社区文章-社区文章'])
# agent.include_router(agent_hasn_comments_router, prefix='/hasn/commentss', tags=['社区评论-社区评论'])
# agent.include_router(agent_hasn_follows_router, prefix='/hasn/followss', tags=['社区关注-社区关注'])
# agent.include_router(agent_hasn_likes_router, prefix='/hasn/likess', tags=['社区点赞-社区点赞'])
# agent.include_router(agent_hasn_collections_router, prefix='/hasn/collectionss', tags=['社区收藏夹-社区收藏夹'])
# agent.include_router(agent_hasn_collection_items_router, prefix='/hasn/collection/itemss', tags=['社区收藏项-社区收藏项'])
agent.include_router(agent_hasn_skill_bundle_router, prefix='/hasn/skill/bundles', tags=['Skill Bundle 定义表（多个 skill 的组合）-Skill Bundle 定义表（多个 skill 的组合）'])
agent.include_router(agent_hasn_task_router, prefix='/hasn/tasks', tags=['任务定义-任务定义'])
agent.include_router(agent_hasn_task_run_router, prefix='/hasn/task/runs', tags=['任务执行记录-任务执行记录'])
agent.include_router(agent_hasn_sessions_router, prefix='/hasn/sessionss', tags=['HASN 会话分层 - 逻辑会话-HASN 会话分层 - 逻辑会话'])
agent.include_router(agent_hasn_session_events_router, prefix='/hasn/session/eventss', tags=['HASN 会话事件-HASN 会话事件'])
agent.include_router(agent_hasn_session_artifacts_router, prefix='/hasn/session/artifactss', tags=['HASN 会话产物-HASN 会话产物'])

# --- 公开（无需认证，仅 Agent 能力发现） ---
from backend.app.hasn.api.v1.open.hasn_agent_capabilities import router as open_hasn_agent_capabilities_router
from backend.app.hasn.api.v1.open.hasn_posts import router as open_hasn_posts_router
from backend.app.hasn.api.v1.open.hasn_articles import router as open_hasn_articles_router
from backend.app.hasn.api.v1.open.hasn_comments import router as open_hasn_comments_router
from backend.app.hasn.api.v1.open.hasn_follows import router as open_hasn_follows_router
from backend.app.hasn.api.v1.open.hasn_likes import router as open_hasn_likes_router
from backend.app.hasn.api.v1.open.hasn_collections import router as open_hasn_collections_router
from backend.app.hasn.api.v1.open.hasn_collection_items import router as open_hasn_collection_items_router
from backend.app.hasn.api.v1.open.hasn_skill_bundle import router as open_hasn_skill_bundle_router
from backend.app.hasn.api.v1.open.hasn_task import router as open_hasn_task_router
from backend.app.hasn.api.v1.open.hasn_task_run import router as open_hasn_task_run_router
from backend.app.hasn.api.v1.open.hasn_sessions import router as open_hasn_sessions_router
from backend.app.hasn.api.v1.open.hasn_session_events import router as open_hasn_session_events_router
from backend.app.hasn.api.v1.open.hasn_session_artifacts import router as open_hasn_session_artifacts_router

open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/open', tags=['HASN 公开接口'])

open_api.include_router(open_hasn_agent_capabilities_router, prefix='/agent/capabilities', tags=['Agent能力发现'])
# 注释掉 codegen 生成的社区表 open_api 路由
# open_api.include_router(open_hasn_posts_router, prefix='/hasn/postss', tags=['社区帖子-社区帖子'])
# open_api.include_router(open_hasn_articles_router, prefix='/hasn/articless', tags=['社区文章-社区文章'])
# open_api.include_router(open_hasn_comments_router, prefix='/hasn/commentss', tags=['社区评论-社区评论'])
# open_api.include_router(open_hasn_follows_router, prefix='/hasn/followss', tags=['社区关注-社区关注'])
# open_api.include_router(open_hasn_likes_router, prefix='/hasn/likess', tags=['社区点赞-社区点赞'])
# open_api.include_router(open_hasn_collections_router, prefix='/hasn/collectionss', tags=['社区收藏夹-社区收藏夹'])
# open_api.include_router(open_hasn_collection_items_router, prefix='/hasn/collection/itemss', tags=['社区收藏项-社区收藏项'])
open_api.include_router(open_hasn_skill_bundle_router, prefix='/hasn/skill/bundles', tags=['Skill Bundle 定义表（多个 skill 的组合）-Skill Bundle 定义表（多个 skill 的组合）'])
open_api.include_router(open_hasn_task_router, prefix='/hasn/tasks', tags=['任务定义-任务定义'])
open_api.include_router(open_hasn_task_run_router, prefix='/hasn/task/runs', tags=['任务执行记录-任务执行记录'])
open_api.include_router(open_hasn_sessions_router, prefix='/hasn/sessionss', tags=['HASN 会话分层 - 逻辑会话-HASN 会话分层 - 逻辑会话'])
open_api.include_router(open_hasn_session_events_router, prefix='/hasn/session/eventss', tags=['HASN 会话事件-HASN 会话事件'])
open_api.include_router(open_hasn_session_artifacts_router, prefix='/hasn/session/artifactss', tags=['HASN 会话产物-HASN 会话产物'])
# open_hasn_nodes_router 已移除（v2.1: 节点注册在 WS 建连时自动完成）

# --- WebSocket 端点（统一节点） ---
from backend.app.hasn.api.ws_node import router as ws_node_router

ws = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn', tags=['HASN WebSocket'])

ws.include_router(ws_node_router)

# --- 用户端业务 API（联系人 + 认证 + 搜索） ---
from backend.app.hasn.api.v1.app.contacts import router as app_contacts_router
from backend.app.hasn.api.v1.app.enterprise import router as enterprise_router
from backend.app.hasn.api.v1.app.hasn_api_keys import router as app_hasn_api_keys_router
from backend.app.hasn.api.v1.app.hasn_auth_api import router as app_hasn_auth_router
from backend.app.hasn.api.v1.app.hasn_nodes import router as app_hasn_nodes_router
from backend.app.hasn.api.v1.app.hasn_owner_api_keys import router as app_hasn_owner_api_keys_router
from backend.app.hasn.api.v1.app.profile import router as app_profile_router
from backend.app.hasn.api.v1.app.search import router as app_users_search_router
from backend.app.hasn.api.v1.app.workbench import router as workbench_router
from backend.app.hasn.api.v1.app.workspace import router as workspace_router
from backend.app.hasn.api.v1.node_control import router as node_control_router

app.include_router(app_contacts_router, tags=['联系人管理'])
app.include_router(app_hasn_auth_router, tags=['HASN认证'])
v1.include_router(enterprise_router, tags=['企业与工作空间'])
v1.include_router(workspace_router, tags=['工作区切换'])
app.include_router(workbench_router, tags=['工作台'])
app.include_router(app_users_search_router, tags=['HASN Users'])
app.include_router(app_profile_router, prefix='/profile', tags=['合并 Profile (sys_user + hasn_humans)'])

# --- IM 业务 API ---
from backend.app.hasn.api.v1.app.hasn_im import router as app_hasn_im_router
from backend.app.hasn.api.v1.app.hasn_posts import router as app_hasn_posts_router
from backend.app.hasn.api.v1.app.hasn_articles import router as app_hasn_articles_router
from backend.app.hasn.api.v1.app.hasn_comments import router as app_hasn_comments_router
from backend.app.hasn.api.v1.app.hasn_follows import router as app_hasn_follows_router
from backend.app.hasn.api.v1.app.hasn_likes import router as app_hasn_likes_router
from backend.app.hasn.api.v1.app.hasn_collections import router as app_hasn_collections_router
from backend.app.hasn.api.v1.app.hasn_collection_items import router as app_hasn_collection_items_router
from backend.app.hasn.api.v1.app.community import router as app_community_router
from backend.app.hasn.api.v1.app.hasn_skill_bundle import router as app_hasn_skill_bundle_router
from backend.app.hasn.api.v1.app.hasn_task import router as app_hasn_task_router
from backend.app.hasn.api.v1.app.hasn_task_run import router as app_hasn_task_run_router
from backend.app.hasn.api.v1.app.hasn_task_api import router as app_hasn_task_api_router
from backend.app.hasn.api.v1.app.hasn_sessions import router as app_hasn_sessions_router
from backend.app.hasn.api.v1.app.hasn_session_events import router as app_hasn_session_events_router
from backend.app.hasn.api.v1.app.hasn_session_artifacts import router as app_hasn_session_artifacts_router
from backend.app.hasn.api.v1.app.hasn_task_sessions import router as app_hasn_task_sessions_router
from backend.app.hasn.api.v1.app.hasn_task_sessions import work_sessions_router

app.include_router(app_hasn_im_router, prefix='/im', tags=['HASN IM 业务'])
app.include_router(app_hasn_api_keys_router, tags=['HASN API Key'])
app.include_router(app_hasn_nodes_router, prefix='/hasn/nodess', tags=['HASN Node 主-HASN Node 主'])
app.include_router(
    app_hasn_skill_bundle_router,
    prefix='/hasn/skill/bundles',
    tags=['Skill Bundle 定义表（多个 skill 的组合）-Skill Bundle 定义表（多个 skill 的组合）'],
)
app.include_router(app_hasn_task_router, prefix='/hasn/tasks', tags=['任务定义-任务定义'])
app.include_router(app_hasn_task_run_router, prefix='/hasn/task/runs', tags=['任务执行记录-任务执行记录'])
app.include_router(
    app_hasn_owner_api_keys_router, prefix='/hasn/owner/api/keyss', tags=['HASN Owner API Key -HASN Owner API Key ']
)
# 社区自定义 API（替代 codegen 生成的 CRUD）
app.include_router(app_community_router, prefix='/community', tags=['社区'])
# 注释掉 codegen 生成的社区表 CRUD 路由，使用自定义社区 API
# app.include_router(app_hasn_posts_router, prefix='/hasn/postss', tags=['社区帖子-社区帖子'])
# app.include_router(app_hasn_articles_router, prefix='/hasn/articless', tags=['社区文章-社区文章'])
# app.include_router(app_hasn_comments_router, prefix='/hasn/commentss', tags=['社区评论-社区评论'])
# app.include_router(app_hasn_follows_router, prefix='/hasn/followss', tags=['社区关注-社区关注'])
# app.include_router(app_hasn_likes_router, prefix='/hasn/likess', tags=['社区点赞-社区点赞'])
# app.include_router(app_hasn_collections_router, prefix='/hasn/collectionss', tags=['社区收藏夹-社区收藏夹'])
# app.include_router(app_hasn_collection_items_router, prefix='/hasn/collection/itemss', tags=['社区收藏项-社区收藏项'])
app.include_router(app_hasn_sessions_router, prefix='/hasn/sessionss', tags=['HASN 会话分层 - 逻辑会话-HASN 会话分层 - 逻辑会话'])
app.include_router(app_hasn_session_events_router, prefix='/hasn/session/eventss', tags=['HASN 会话事件-HASN 会话事件'])
app.include_router(app_hasn_session_artifacts_router, prefix='/hasn/session/artifactss', tags=['HASN 会话产物-HASN 会话产物'])
app.include_router(app_hasn_task_sessions_router, tags=['任务系统 Session API'])
app.include_router(app_hasn_task_api_router, tags=['任务系统 Task API'])
v1.include_router(work_sessions_router, tags=['外部 APP 工作会话'])
v1.include_router(node_control_router, tags=['HASN Node 控制平面'])
# 注释掉 codegen 生成的社区表 admin 路由
# v1.include_router(admin_hasn_posts_router, prefix='/hasn/postss', tags=['社区帖子-社区帖子'])
# v1.include_router(admin_hasn_articles_router, prefix='/hasn/articless', tags=['社区文章-社区文章'])
# v1.include_router(admin_hasn_comments_router, prefix='/hasn/commentss', tags=['社区评论-社区评论'])
# v1.include_router(admin_hasn_follows_router, prefix='/hasn/followss', tags=['社区关注-社区关注'])
# v1.include_router(admin_hasn_likes_router, prefix='/hasn/likess', tags=['社区点赞-社区点赞'])
# v1.include_router(admin_hasn_collections_router, prefix='/hasn/collectionss', tags=['社区收藏夹-社区收藏夹'])
# v1.include_router(admin_hasn_collection_items_router, prefix='/hasn/collection/itemss', tags=['社区收藏项-社区收藏项'])
v1.include_router(admin_hasn_skill_bundle_router, prefix='/hasn/skill/bundles', tags=['Skill Bundle 定义表（多个 skill 的组合）-Skill Bundle 定义表（多个 skill 的组合）'])
v1.include_router(admin_hasn_task_router, prefix='/hasn/tasks', tags=['任务定义-任务定义'])
v1.include_router(admin_hasn_task_run_router, prefix='/hasn/task/runs', tags=['任务执行记录-任务执行记录'])
v1.include_router(admin_hasn_sessions_router, prefix='/hasn/sessionss', tags=['HASN 会话分层 - 逻辑会话-HASN 会话分层 - 逻辑会话'])
v1.include_router(admin_hasn_session_events_router, prefix='/hasn/session/eventss', tags=['HASN 会话事件-HASN 会话事件'])
v1.include_router(admin_hasn_session_artifacts_router, prefix='/hasn/session/artifactss', tags=['HASN 会话产物-HASN 会话产物'])
