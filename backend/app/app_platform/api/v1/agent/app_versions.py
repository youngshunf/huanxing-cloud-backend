"""App 版本 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_versions import (
    CreateAppVersionsParam,
    UpdateAppVersionsParam,
)
from backend.app.app_platform.service.app_versions_service import app_versions_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='App 版本列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_versionss(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await app_versions_service.get_list(db=db)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建App 版本',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_versions(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateAppVersionsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await app_versions_service.create(db=db, obj=obj)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取App 版本详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_versions(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App 版本 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_versions = await app_versions_service.get(db=db, pk=pk)
    if app_versions.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该App 版本')
    return response_base.success(data=app_versions)

@router.put(
    '/{pk}',
    summary='更新App 版本',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_versions(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App 版本 ID')],
    obj: UpdateAppVersionsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_versions = await app_versions_service.get(db=db, pk=pk)
    if app_versions.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该App 版本')
    count = await app_versions_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除App 版本',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_versions(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='App 版本 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_versions = await app_versions_service.get(db=db, pk=pk)
    if app_versions.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App 版本')
    from backend.app.app_platform.schema.app_versions import DeleteAppVersionsParam
    count = await app_versions_service.delete(db=db, obj=DeleteAppVersionsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
