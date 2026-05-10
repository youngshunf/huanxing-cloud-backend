from __future__ import annotations

from fastapi import APIRouter

from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth

router = APIRouter()


@router.get('/status', summary='Agent 触达接口预留状态', dependencies=[DependsAgentAuth])
async def status() -> ResponseModel:
    return response_base.success(data={'status': 'reserved'})
