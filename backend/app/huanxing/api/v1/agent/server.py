"""唤星 Agent 服务器上报 API

路径前缀: /api/v1/huanxing/agent/servers
认证方式: X-Agent-Key（DependsAgentAuth）

供 Guardian Agent 启动时注册服务器，并定期心跳上报状态。
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.huanxing.schema.huanxing_server import (
    AgentRegisterServerParam,
    AgentHeartbeatParam,
    AgentRegisterServerResponse,
    HeartbeatResponse,
)
from backend.app.huanxing.service.huanxing_server_service import huanxing_server_service
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.database.db import CurrentSessionTransaction

router = APIRouter()


@router.post(
    '/register',
    summary='注册/更新服务器信息（Agent启动时调用）',
    dependencies=[DependsAgentAuth],
)
async def agent_register_server(
    db: CurrentSessionTransaction,
    request: Request,
    obj: AgentRegisterServerParam,
) -> ResponseSchemaModel[AgentRegisterServerResponse]:
    """Guardian Agent 启动时调用，注册或更新服务器信息。

    - 如果 server_id 已存在，更新信息
    - 如果不存在，创建新记录
    - 自动获取客户端 IP
    """
    # 获取客户端真实 IP
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"

    result = await huanxing_server_service.agent_register(db=db, obj=obj, client_ip=client_ip)
    return response_base.success(data=result)


@router.post(
    '/{server_id}/heartbeat',
    summary='服务器心跳上报',
    description='Guardian 定期调用，上报服务器状态（Gateway状态、用户数、CPU/内存等）',
    dependencies=[DependsAgentAuth],
)
async def agent_heartbeat(
    db: CurrentSessionTransaction,
    server_id: Annotated[str, Path(description='服务器唯一标识')],
    obj: AgentHeartbeatParam,
) -> ResponseSchemaModel[HeartbeatResponse]:
    """Guardian Agent 定期心跳上报。"""
    result = await huanxing_server_service.heartbeat(db=db, server_id=server_id, obj=obj)
    return response_base.success(data=result)
