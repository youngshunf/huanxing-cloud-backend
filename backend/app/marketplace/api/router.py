from fastapi import APIRouter

from backend.app.marketplace.api.v1.marketplace_category import router as marketplace_category_router
from backend.app.marketplace.api.v1.marketplace_skill import router as marketplace_skill_router
from backend.app.marketplace.api.v1.marketplace_skill_version import router as marketplace_skill_version_router
from backend.app.marketplace.api.v1.marketplace_app import router as marketplace_app_router
from backend.app.marketplace.api.v1.marketplace_app_version import router as marketplace_app_version_router
from backend.app.marketplace.api.v1.marketplace_download import router as marketplace_download_router
from backend.app.marketplace.api.v1.download import router as download_router
from backend.app.marketplace.api.v1.sync import router as sync_router
from backend.app.marketplace.api.v1.search import router as search_router
from backend.app.marketplace.api.v1.client import router as client_router  # 桌面端公开 API
from backend.app.marketplace.api.v1.publish import router as publish_router  # 发布 API
from backend.app.marketplace.api.v1.webhook import router as webhook_router  # GitHub Webhook
from backend.app.marketplace.api.v1.admin.marketplace_skill import router as admin_marketplace_skill_router
from backend.app.marketplace.api.v1.admin.marketplace_skill_version import router as admin_marketplace_skill_version_router
from backend.app.marketplace.api.v1.admin.marketplace_category import router as admin_marketplace_category_router
from backend.app.marketplace.api.v1.admin.marketplace_sync_log import router as admin_marketplace_sync_log_router
from backend.app.marketplace.api.v1.admin.marketplace_download_history import router as admin_marketplace_download_history_router
from backend.app.marketplace.api.v1.admin.sync_management import router as admin_sync_management_router
from backend.app.marketplace.api.v1.admin.skill_management import router as admin_skill_management_router
from backend.core.conf import settings

# 管理端 API（需要认证）
v1 = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/marketplace', tags=['技能市场'])

v1.include_router(marketplace_category_router, prefix='/categories')
v1.include_router(marketplace_skill_version_router, prefix='/skills/versions')  # 更具体的路由放前面
v1.include_router(marketplace_skill_router, prefix='/skills')
v1.include_router(marketplace_app_version_router, prefix='/apps/versions')  # 更具体的路由放前面
v1.include_router(marketplace_app_router, prefix='/apps')
v1.include_router(download_router, prefix='/download')  # 下载 API
v1.include_router(sync_router, prefix='/sync')  # 同步 API
v1.include_router(search_router, prefix='/search')  # 搜索 API
v1.include_router(webhook_router, prefix='/webhook')  # GitHub Webhook（公开，内部验证签名）
v1.include_router(marketplace_download_router, prefix='/downloads')  # 下载记录管理
v1.include_router(admin_marketplace_skill_router, prefix='/marketplace/skills', tags=['技能市场技能-技能市场技能'])
v1.include_router(admin_marketplace_skill_version_router, prefix='/marketplace/skill/versions', tags=['技能版本-技能版本'])
v1.include_router(admin_marketplace_category_router, prefix='/marketplace/categorys', tags=['技能市场分类-技能市场分类'])
v1.include_router(admin_marketplace_sync_log_router, prefix='/marketplace/sync/logs', tags=['技能市场同步日志-技能市场同步日志'])
v1.include_router(admin_marketplace_download_history_router, prefix='/marketplace/download/historys', tags=['技能市场下载历史-技能市场下载历史'])
v1.include_router(admin_sync_management_router, prefix='/admin/sync', tags=['技能市场-同步管理'])
v1.include_router(admin_skill_management_router, prefix='/admin/skills', tags=['技能市场-技能管理'])

# 桌面端公开 API（不需要认证）
# 注册到 /api/v1/marketplace/client 路径下
client = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/marketplace/client', tags=['市场-桌面端'])
client.include_router(client_router)

# 发布 API（需要 API Key 认证）
# 注册到 /api/v1/marketplace/publish 路径下
publish = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/marketplace/publish', tags=['市场-发布'])
publish.include_router(publish_router)


# --- 用户端（仅 JWT） ---
from backend.app.marketplace.api.v1.app.marketplace_sync_log import router as app_marketplace_sync_log_router
from backend.app.marketplace.api.v1.app.marketplace_download_history import router as app_marketplace_download_history_router

app = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/marketplace/app', tags=['技能市场同步日志'])

app.include_router(app_marketplace_sync_log_router, prefix='/marketplace/sync/logs', tags=['技能市场同步日志-技能市场同步日志'])
app.include_router(app_marketplace_download_history_router, prefix='/marketplace/download/historys', tags=['技能市场下载历史-技能市场下载历史'])

# --- Agent（Agent Key） ---
from backend.app.marketplace.api.v1.agent.marketplace_sync_log import router as agent_marketplace_sync_log_router
from backend.app.marketplace.api.v1.agent.marketplace_download_history import router as agent_marketplace_download_history_router

agent = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/marketplace/agent', tags=['技能市场同步日志'])

agent.include_router(agent_marketplace_sync_log_router, prefix='/marketplace/sync/logs', tags=['技能市场同步日志-技能市场同步日志'])
agent.include_router(agent_marketplace_download_history_router, prefix='/marketplace/download/historys', tags=['技能市场下载历史-技能市场下载历史'])

# --- 公开（无需认证） ---
from backend.app.marketplace.api.v1.open.marketplace_sync_log import router as open_marketplace_sync_log_router
from backend.app.marketplace.api.v1.open.marketplace_download_history import router as open_marketplace_download_history_router
from backend.app.marketplace.api.v1.open.marketplace_skills import router as open_marketplace_skills_router

open_api = APIRouter(prefix=f'{settings.FASTAPI_API_V1_PATH}/marketplace/open', tags=['技能市场'])

open_api.include_router(open_marketplace_skills_router, prefix='/skills', tags=['技能市场-公开API'])
open_api.include_router(open_marketplace_sync_log_router, prefix='/marketplace/sync/logs', tags=['技能市场同步日志-技能市场同步日志'])
open_api.include_router(open_marketplace_download_history_router, prefix='/marketplace/download/historys', tags=['技能市场下载历史-技能市场下载历史'])