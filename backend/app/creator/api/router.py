from fastapi import APIRouter

from backend.app.creator.api.v1.hx_creator_project import router as hx_creator_project_router
from backend.app.creator.api.v1.hx_creator_profile import router as hx_creator_profile_router
from backend.app.creator.api.v1.hx_creator_account import router as hx_creator_account_router
from backend.app.creator.api.v1.hx_creator_content import router as hx_creator_content_router
from backend.app.creator.api.v1.hx_creator_content_stage import router as hx_creator_content_stage_router
from backend.app.creator.api.v1.hx_creator_publish import router as hx_creator_publish_router
from backend.app.creator.api.v1.hx_creator_competitor import router as hx_creator_competitor_router
from backend.app.creator.api.v1.hx_creator_draft import router as hx_creator_draft_router
from backend.app.creator.api.v1.hx_creator_media import router as hx_creator_media_router
from backend.app.creator.api.v1.hx_creator_viral_pattern import router as hx_creator_viral_pattern_router
from backend.app.creator.api.v1.hx_creator_hot_topic import router as hx_creator_hot_topic_router
from backend.app.creator.api.v1.hx_creator_topic import router as hx_creator_topic_router

# Agent 端 API
from backend.app.creator.api.v1.agent.project import router as agent_project_router
from backend.app.creator.api.v1.agent.profile import router as agent_profile_router
from backend.app.creator.api.v1.agent.account import router as agent_account_router
from backend.app.creator.api.v1.agent.content import router as agent_content_router
from backend.app.creator.api.v1.agent.publish import router as agent_publish_router
from backend.app.creator.api.v1.agent.analytics import router as agent_analytics_router
from backend.app.creator.api.v1.agent.media import router as agent_media_router
from backend.app.creator.api.v1.agent.topic import router as agent_topic_router

# 用户端 API
from backend.app.creator.api.v1.app.project import router as app_project_router
from backend.app.creator.api.v1.app.content import router as app_content_router
from backend.app.creator.api.v1.app.publish import router as app_publish_router
from backend.app.creator.api.v1.app.analytics import router as app_analytics_router
from backend.app.creator.api.v1.app.topic import router as app_topic_router

from backend.core.conf import settings

# ========================================
# 管理端 API（JWT + RBAC）
# 路径前缀: /api/v1/creator/
# ========================================
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/creator')

v1.include_router(hx_creator_project_router, prefix='/projects', tags=['创作项目'])
v1.include_router(hx_creator_profile_router, prefix='/profiles', tags=['账号画像'])
v1.include_router(hx_creator_account_router, prefix='/accounts', tags=['平台账号'])
v1.include_router(hx_creator_content_router, prefix='/contents', tags=['内容管理'])
v1.include_router(hx_creator_content_stage_router, prefix='/content-stages', tags=['内容阶段'])
v1.include_router(hx_creator_publish_router, prefix='/publishes', tags=['发布记录'])
v1.include_router(hx_creator_competitor_router, prefix='/competitors', tags=['竞品分析'])
v1.include_router(hx_creator_draft_router, prefix='/drafts', tags=['草稿箱'])
v1.include_router(hx_creator_media_router, prefix='/media', tags=['素材库'])
v1.include_router(hx_creator_viral_pattern_router, prefix='/viral-patterns', tags=['爆款模式'])
v1.include_router(hx_creator_hot_topic_router, prefix='/hot-topics', tags=['热榜快照'])
v1.include_router(hx_creator_topic_router, prefix='/topics', tags=['选题推荐'])

# ========================================
# Agent 端 API（仅 JWT，无 RBAC）
# 路径前缀: /api/v1/creator/agent/
# ========================================
agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/creator/agent', tags=['创作中心Agent'])

agent.include_router(agent_project_router, prefix='/projects', tags=['创作Agent-项目'])
agent.include_router(agent_profile_router, prefix='/profiles', tags=['创作Agent-画像'])
agent.include_router(agent_account_router, prefix='/accounts', tags=['创作Agent-账号'])
agent.include_router(agent_content_router, prefix='/contents', tags=['创作Agent-内容'])
agent.include_router(agent_publish_router, prefix='/publishes', tags=['创作Agent-发布'])
agent.include_router(agent_analytics_router, prefix='/analytics', tags=['创作Agent-分析'])
agent.include_router(agent_media_router, prefix='/media', tags=['创作Agent-素材'])
agent.include_router(agent_topic_router, prefix='/topics', tags=['创作Agent-选题'])

# ========================================
# 用户端 API（JWT）
# 路径前缀: /api/v1/creator/app/
# ========================================
app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/creator/app', tags=['创作中心用户端'])

app.include_router(app_project_router, prefix='/projects', tags=['用户端-项目'])
app.include_router(app_content_router, prefix='/contents', tags=['用户端-内容'])
app.include_router(app_publish_router, prefix='/publishes', tags=['用户端-发布'])
app.include_router(app_analytics_router, prefix='/analytics', tags=['用户端-分析'])
app.include_router(app_topic_router, prefix='/topics', tags=['用户端-选题'])
