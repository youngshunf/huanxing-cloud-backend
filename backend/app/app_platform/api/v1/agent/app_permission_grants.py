"""权限授予记录 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_permission_grants import (
    CreateAppPermissionGrantsParam,
    UpdateAppPermissionGrantsParam,
)
from backend.app.app_platform.service.app_permission_grants_service import app_permission_grants_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='权限授予记录列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_permission_grantss(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await app_permission_grants_service.get_list(db=db)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建权限授予记录',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_permission_grants(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateAppPermissionGrantsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await app_permission_grants_service.create(db=db, obj=obj)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取权限授予记录详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_permission_grants(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='权限授予记录 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    if app_permission_grants.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该权限授予记录')
    return response_base.success(data=app_permission_grants)

@router.put(
    '/{pk}',
    summary='更新权限授予记录',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_permission_grants(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='权限授予记录 ID')],
    obj: UpdateAppPermissionGrantsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    if app_permission_grants.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该权限授予记录')
    count = await app_permission_grants_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除权限授予记录',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_permission_grants(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='权限授予记录 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    if app_permission_grants.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该权限授予记录')
    from backend.app.app_platform.schema.app_permission_grants import DeleteAppPermissionGrantsParam
    count = await app_permission_grants_service.delete(db=db, obj=DeleteAppPermissionGrantsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
