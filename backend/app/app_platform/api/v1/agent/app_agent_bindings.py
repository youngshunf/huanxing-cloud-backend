"""Installation 绑定的 Agent 列 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_agent_bindings import (
    CreateAppAgentBindingsParam,
    UpdateAppAgentBindingsParam,
)
from backend.app.app_platform.service.app_agent_bindings_service import app_agent_bindings_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='Installation 绑定的 Agent 列列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_agent_bindingss(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await app_agent_bindings_service.get_list(db=db)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建Installation 绑定的 Agent 列',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_agent_bindings(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateAppAgentBindingsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await app_agent_bindings_service.create(db=db, obj=obj)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取Installation 绑定的 Agent 列详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_agent_bindings(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    if app_agent_bindings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该Installation 绑定的 Agent 列')
    return response_base.success(data=app_agent_bindings)

@router.put(
    '/{pk}',
    summary='更新Installation 绑定的 Agent 列',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_agent_bindings(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')],
    obj: UpdateAppAgentBindingsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    if app_agent_bindings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该Installation 绑定的 Agent 列')
    count = await app_agent_bindings_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除Installation 绑定的 Agent 列',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_agent_bindings(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    if app_agent_bindings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Installation 绑定的 Agent 列')
    from backend.app.app_platform.schema.app_agent_bindings import DeleteAppAgentBindingsParam
    count = await app_agent_bindings_service.delete(db=db, obj=DeleteAppAgentBindingsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
