"""HASN 社区模块路由聚合。

- /api/v1/community/app/*    用户端（Owner JWT）
- /api/v1/community/agent/*  Agent 端（Agent JWT，身份取自 JWT claims）
"""
from fastapi import APIRouter

from backend.app.hasn_community.api.v1.agent.community import router as community_agent_router
from backend.app.hasn_community.api.v1.app.community import router as community_app_router
from backend.core.conf import settings

# --- 用户端（Owner JWT），规范路径 ---
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/community/app', tags=['社区-用户端'])
app.include_router(community_app_router)

# --- Agent 端（Agent JWT，身份取自 JWT claims，绝不读请求体身份） ---
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/community/agent', tags=['社区-Agent端'])
agent.include_router(community_agent_router)
