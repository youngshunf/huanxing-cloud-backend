from backend.app.hermes.api.router import v1 as hermes_v1, app as hermes_app, internal as hermes_internal
from backend.app.hasn.api.router import (, v1 as hasn_v1, app as hasn_app, agent as hasn_agent, open_api as hasn_open, v1 as hasn_v1, app as hasn_app, agent as hasn_agent, open_api as hasn_open, v1 as hasn_v1, app as hasn_app, agent as hasn_agent, open_api as hasn_open, v1 as hasn_v1, app as hasn_app, agent as hasn_agent, open_api as hasn_open, v1 as hasn_v1, app as hasn_app, agent as hasn_agent, open_api as hasn_open, v1 as hasn_v1, app as hasn_app, agent as hasn_agent, open_api as hasn_open, v1 as hasn_v1, app as hasn_app, agent as hasn_agent, open_api as hasn_open
    ai_native as hasn_ai_native,
    agent as hasn_agent,
    app as hasn_app,
    open_api as hasn_open,
    v1 as hasn_v1,
    ws as hasn_ws,
)
from backend.app.lead_automation.api.router import (
    agent as lead_automation_agent,
    app as lead_automation_app,
    open_api as lead_automation_open,
    v1 as lead_automation_v1,
)
from fastapi import APIRouter
from backend.app.admin.api.router import v1 as admin_v1, client as admin_client
from backend.app.llm.api.router import v1 as llm_v1, app as llm_app
from backend.app.task.api.router import v1 as task_v1
from backend.app.openclaw.api.router import v1 as openclaw_v1
from backend.app.projects.api.router import v1 as projects_v1
from backend.app.user_tier.api.router import v1 as user_tier_v1, app as user_tier_app, open_api as user_tier_open, agent as user_tier_agent
from backend.app.marketplace.api.router import v1 as marketplace_v1, client as marketplace_client, publish as marketplace_publish
from backend.app.pay.api.router import v1 as pay_v1, app as pay_app, open_api as pay_open
from backend.app.huanxing.api.router import v1 as huanxing_v1, app as huanxing_app, open_api as huanxing_open, agent as huanxing_agent, user_api as huanxing_user
from backend.app.api.v1.app import app_router as mobile_app_v1_router
from backend.app.api.v1.auth import auth_router as mobile_auth_v1_router

router = APIRouter()

router.include_router(admin_v1)
router.include_router(task_v1)
router.include_router(llm_v1)
router.include_router(llm_app)
router.include_router(openclaw_v1)  # Openclaw Gateway API
router.include_router(lead_automation_v1)
router.include_router(lead_automation_app)
router.include_router(lead_automation_agent)
router.include_router(lead_automation_open)

router.include_router(projects_v1)
router.include_router(user_tier_v1)
router.include_router(user_tier_app)      # 订阅积分-用户端 API
router.include_router(user_tier_open)     # 订阅积分-公开 API
router.include_router(user_tier_agent)    # 订阅积分-Agent API
router.include_router(marketplace_v1)
router.include_router(marketplace_client)  # 桌面端市场公开 API
router.include_router(marketplace_publish)  # 发布 API
router.include_router(admin_client)       # 桌面端版本检测公开 API

# 支付（独立模块）
router.include_router(pay_v1)             # 支付管理 API
router.include_router(pay_app)            # 支付-用户端 API
router.include_router(pay_open)           # 支付-公开回调 API

# 唤星
router.include_router(huanxing_v1)
router.include_router(huanxing_app)       # 唤星用户端 API
router.include_router(huanxing_open)      # 唤星公开 API（支付回调等）
router.include_router(huanxing_agent)     # 唤星Agent API
router.include_router(huanxing_user)      # 唤星用户级API（Owner Key 认证）

# HASN（统一模块，合并原 hasn / hasn_core / hasn_social）
router.include_router(hasn_v1)            # HASN 管理端 API
router.include_router(hasn_app)           # HASN 用户端 API
router.include_router(hasn_agent)         # HASN Agent API
router.include_router(hasn_open)          # HASN 公开 API
router.include_router(hasn_ws)            # HASN WebSocket 端点
router.include_router(hasn_ai_native)      # AI-Native 应用平台 API


# Hermes（后台管理 CRUD；用户端 /hermes/app/agents 后续手写编排 API）
router.include_router(hermes_v1)
router.include_router(hermes_app)
router.include_router(hermes_internal)    # runtime ↔ backend 内部 service token 调用（X-Internal-Token）

# 移动端 App API (M1: /api/v1/app/...)
router.include_router(mobile_app_v1_router)  # 移动端用户端 API (owner_api_keys/current 等)
router.include_router(mobile_auth_v1_router)  # 移动端认证 API (/api/v1/auth/logout 等)
