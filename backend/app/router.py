from backend.app.huanxing.api.router import v1 as huanxing_v1, app as huanxing_app, open_api as huanxing_open, agent as huanxing_agent
from backend.app.marketplace.api.router import v1 as marketplace_v1, client as marketplace_client, publish as marketplace_publish
from backend.app.pay.api.router import v1 as pay_v1, app as pay_app, open_api as pay_open
from backend.app.user_tier.api.router import v1 as user_tier_v1, app as user_tier_app, open_api as user_tier_open, agent as user_tier_agent
from backend.app.projects.api.router import v1 as projects_v1
from backend.app.openclaw.api.router import v1 as openclaw_v1
from fastapi import APIRouter

from backend.app.admin.api.router import v1 as admin_v1, client as admin_client
from backend.app.llm.api.router import v1 as llm_v1
from backend.app.task.api.router import v1 as task_v1

# HASN Modules
from backend.app.hasn_core.api.router import v1 as hasn_core_v1
from backend.app.hasn_social.api.router import v1 as hasn_social_v1

router = APIRouter()

router.include_router(admin_v1)
router.include_router(task_v1)
router.include_router(llm_v1)
router.include_router(openclaw_v1)  # Openclaw Gateway API

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

# HASN
router.include_router(hasn_core_v1)
router.include_router(hasn_social_v1)
