"""唤星 Agent 数据看板 API

路径前缀: /api/v1/huanxing/agent/dashboard
认证方式: X-Agent-Key（DependsAgentAuth）
"""
from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.huanxing.schema.huanxing_server import DashboardResponse
from backend.app.huanxing.service.huanxing_server_service import huanxing_server_service
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='唤星数据看板（Agent端）',
    description='返回全局/按服务器的统计数据：用户总数、活跃数、服务器数、按模板/服务器分布等',
    dependencies=[DependsAgentAuth],
)
async def agent_get_dashboard(
    db: CurrentSession,
    server_id: Annotated[str | None, Query(description='按服务器筛选（可选）')] = None,
) -> ResponseSchemaModel[DashboardResponse]:
    dashboard = await huanxing_server_service.get_dashboard(db=db, server_id=server_id)
    return response_base.success(data=dashboard)
