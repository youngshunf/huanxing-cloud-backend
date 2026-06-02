"""统一通知服务路由聚合。

- /api/v1/notifications/app/*    用户端（Owner JWT）——通知中心（D1 权威视图）+ 主人偏好
- /api/v1/notifications/agent/*  Agent 端（Agent JWT，身份取自 JWT claims）
- /api/v1/notifications/admin/*  管理端（Admin JWT，只读运维）

设计事实源：docs/hasn-node设计文档/通知系统统一设计/00-统一通知服务设计.md §9。
"""
from fastapi import APIRouter

from backend.app.notification.api.v1.admin.notification import router as notification_admin_router
from backend.app.notification.api.v1.agent.notification import router as notification_agent_router
from backend.app.notification.api.v1.app.notification import router as notification_app_router
from backend.core.conf import settings

# --- 用户端（Owner JWT） ---
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/notifications/app', tags=['通知-用户端'])
app.include_router(notification_app_router)

# --- Agent 端（Agent JWT） ---
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/notifications/agent', tags=['通知-Agent端'])
agent.include_router(notification_agent_router)

# --- Admin 端（Admin JWT，只读运维） ---
admin = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/notifications/admin', tags=['通知-管理端'])
admin.include_router(notification_admin_router)
