"""App Tool 定义 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_tools import (
    CreateAppToolsParam,
    UpdateAppToolsParam,
)
from backend.app.app_platform.service.app_tools_service import app_tools_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='App Tool 定义列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_toolss(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await app_tools_service.get_list(db=db)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建App Tool 定义',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_tools(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateAppToolsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await app_tools_service.create(db=db, obj=obj)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取App Tool 定义详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_tools(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App Tool 定义 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_tools = await app_tools_service.get(db=db, pk=pk)
    if app_tools.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该App Tool 定义')
    return response_base.success(data=app_tools)

@router.put(
    '/{pk}',
    summary='更新App Tool 定义',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_tools(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App Tool 定义 ID')],
    obj: UpdateAppToolsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_tools = await app_tools_service.get(db=db, pk=pk)
    if app_tools.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该App Tool 定义')
    count = await app_tools_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除App Tool 定义',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_tools(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App Tool 定义 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_tools = await app_tools_service.get(db=db, pk=pk)
    if app_tools.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App Tool 定义')
    from backend.app.app_platform.schema.app_tools import DeleteAppToolsParam
    count = await app_tools_service.delete(db=db, obj=DeleteAppToolsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
