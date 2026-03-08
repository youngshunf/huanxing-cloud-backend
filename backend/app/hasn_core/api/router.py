from fastapi import APIRouter
from backend.core.conf import settings

# 业务接口
from backend.app.hasn_core.api.v1.auth import router as auth_router
from backend.app.hasn_core.api.v1.ws_sync import router as sync_router
from backend.app.hasn_core.api.v1.identity import router as identity_router
from backend.app.hasn_core.api.v1.messages import router as messages_router
from backend.app.hasn_core.api.v1.conversations import router as conversations_router

# 管理端 CRUD 接口
from backend.app.hasn_core.api.v1.admin.hasn_humans import router as admin_humans_router
from backend.app.hasn_core.api.v1.admin.hasn_agents import router as admin_agents_router
from backend.app.hasn_core.api.v1.admin.hasn_conversations import router as admin_conversations_router
from backend.app.hasn_core.api.v1.admin.hasn_group_members import router as admin_group_members_router
from backend.app.hasn_core.api.v1.admin.hasn_messages import router as admin_messages_router
from backend.app.hasn_core.api.v1.admin.hasn_notifications import router as admin_notifications_router
from backend.app.hasn_core.api.v1.admin.hasn_audit_log import router as admin_audit_log_router

# 业务路由
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn')
v1.include_router(auth_router)
v1.include_router(sync_router)
v1.include_router(identity_router)
v1.include_router(messages_router)
v1.include_router(conversations_router)

# 管理端路由 (prefix: /api/v1/hasn/admin/xxx)
v1.include_router(admin_humans_router, prefix='/admin/humans', tags=['HASN用户管理'])
v1.include_router(admin_agents_router, prefix='/admin/agents', tags=['HASN Agent管理'])
v1.include_router(admin_conversations_router, prefix='/admin/conversations', tags=['HASN会话管理'])
v1.include_router(admin_group_members_router, prefix='/admin/group-members', tags=['HASN群成员管理'])
v1.include_router(admin_messages_router, prefix='/admin/messages', tags=['HASN消息管理'])
v1.include_router(admin_notifications_router, prefix='/admin/notifications', tags=['HASN通知管理'])
v1.include_router(admin_audit_log_router, prefix='/admin/audit-log', tags=['HASN审计日志'])
