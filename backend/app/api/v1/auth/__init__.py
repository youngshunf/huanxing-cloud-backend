"""M1 移动端 Auth 聚合路由.

挂载位置: /api/v1/auth

目前包含:
- POST /logout — JWT 吊销端点 (B2, 对齐 docs/架构设计/移动端/05 §16.1)
- POST /agent-token/refresh — Agent JWT 刷新端点
"""
from fastapi import APIRouter

from backend.app.api.v1.auth.agent_token_refresh import router as agent_token_refresh_router
from backend.app.api.v1.auth.logout import router as logout_router
from backend.core.conf import settings

auth_router = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/auth', tags=['移动端 Auth'])
auth_router.include_router(logout_router)
auth_router.include_router(agent_token_refresh_router)
