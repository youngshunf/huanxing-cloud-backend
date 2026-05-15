"""App Event 定义 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_events import (
    CreateAppEventsParam,
    UpdateAppEventsParam,
)
from backend.app.app_platform.service.app_events_service import app_events_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='App Event 定义列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_eventss(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await app_events_service.get_list(db=db)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建App Event 定义',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_events(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateAppEventsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await app_events_service.create(db=db, obj=obj)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取App Event 定义详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_events(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App Event 定义 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_events = await app_events_service.get(db=db, pk=pk)
    if app_events.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该App Event 定义')
    return response_base.success(data=app_events)

@router.put(
    '/{pk}',
    summary='更新App Event 定义',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_events(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App Event 定义 ID')],
    obj: UpdateAppEventsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_events = await app_events_service.get(db=db, pk=pk)
    if app_events.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该App Event 定义')
    count = await app_events_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除App Event 定义',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_events(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App Event 定义 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_events = await app_events_service.get(db=db, pk=pk)
    if app_events.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App Event 定义')
    from backend.app.app_platform.schema.app_events import DeleteAppEventsParam
    count = await app_events_service.delete(db=db, obj=DeleteAppEventsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
