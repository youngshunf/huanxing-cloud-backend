"""应用市场列表 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_listings import (
    CreateAppListingsParam,
    UpdateAppListingsParam,
)
from backend.app.app_platform.service.app_listings_service import app_listings_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='应用市场列表列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_listingss(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await app_listings_service.get_list(db=db)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建应用市场列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_listings(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateAppListingsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await app_listings_service.create(db=db, obj=obj)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取应用市场列表详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_listings(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='应用市场列表 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该应用市场列表')
    return response_base.success(data=app_listings)

@router.put(
    '/{pk}',
    summary='更新应用市场列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_listings(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
    obj: UpdateAppListingsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该应用市场列表')
    count = await app_listings_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除应用市场列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_listings(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='应用市场列表 ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用市场列表')
    from backend.app.app_platform.schema.app_listings import DeleteAppListingsParam
    count = await app_listings_service.delete(db=db, obj=DeleteAppListingsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
