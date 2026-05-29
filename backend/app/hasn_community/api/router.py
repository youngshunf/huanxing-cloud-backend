"""HASN 社区模块路由聚合。

- /api/v1/community/app/*        用户端（Owner JWT），规范路径
- /api/v1/hasn/app/community/*   兼容别名（daemon 过渡期使用，daemon 切换到规范路径后删除）
- /api/v1/community/agent/*      Agent 端（Agent JWT）—— Phase 4 接入
"""
from fastapi import APIRouter

from backend.app.hasn_community.api.v1.agent.community import router as community_agent_router
from backend.app.hasn_community.api.v1.app.community import router as community_app_router
from backend.core.conf import settings

# --- 用户端（Owner JWT），规范路径 ---
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/community/app', tags=['社区-用户端'])
app.include_router(community_app_router)

# --- 兼容别名：旧 /api/v1/hasn/app/community/*（daemon 过渡期；切换后删除） ---
app_compat = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/hasn/app/community', tags=['社区-用户端（兼容别名）'])
app_compat.include_router(community_app_router)

# --- Agent 端（Agent JWT，身份取自 JWT claims，绝不读请求体身份） ---
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/community/agent', tags=['社区-Agent端'])
agent.include_router(community_agent_router)
