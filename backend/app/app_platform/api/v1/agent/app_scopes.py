"""应用权限定义表（{domain}.* namespace） - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_scopes import (
    CreateAppScopesParam,
    UpdateAppScopesParam,
)
from backend.app.app_platform.service.app_scopes_service import app_scopes_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='应用权限定义表（{domain}.* namespace）列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_scopess(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await app_scopes_service.get_list(db=db)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建应用权限定义表（{domain}.* namespace）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_scopes(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateAppScopesParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await app_scopes_service.create(db=db, obj=obj)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取应用权限定义表（{domain}.* namespace）详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_scopes(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    if app_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该应用权限定义表（{domain}.* namespace）')
    return response_base.success(data=app_scopes)

@router.put(
    '/{pk}',
    summary='更新应用权限定义表（{domain}.* namespace）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_scopes(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')],
    obj: UpdateAppScopesParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    if app_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该应用权限定义表（{domain}.* namespace）')
    count = await app_scopes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除应用权限定义表（{domain}.* namespace）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_scopes(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    if app_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用权限定义表（{domain}.* namespace）')
    from backend.app.app_platform.schema.app_scopes import DeleteAppScopesParam
    count = await app_scopes_service.delete(db=db, obj=DeleteAppScopesParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
