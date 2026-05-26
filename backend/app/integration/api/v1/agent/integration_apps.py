"""第三方应用集成配置 - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.integration.schema.integration_apps import (
    CreateIntegrationAppsParam,
    UpdateIntegrationAppsParam,
)
from backend.app.integration.service.integration_apps_service import integration_apps_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='第三方应用集成配置列表',
    dependencies=[DependsAgentJwtAuth],
    name='agent_list_integration_apps',
)
async def agent_list_integration_apps(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await integration_apps_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建第三方应用集成配置',
    dependencies=[DependsAgentJwtAuth],
    name='agent_create_integration_apps',
)
async def agent_create_integration_apps(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateIntegrationAppsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await integration_apps_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取第三方应用集成配置详情',
    dependencies=[DependsAgentJwtAuth],
    name='agent_get_integration_apps',
)
async def agent_get_integration_apps(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='第三方应用集成配置 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if integration_apps.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该第三方应用集成配置')
    return response_base.success(data=integration_apps)


@router.put(
    '/{pk}',
    summary='更新第三方应用集成配置',
    dependencies=[DependsAgentJwtAuth],
    name='agent_update_integration_apps',
)
async def agent_update_integration_apps(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='第三方应用集成配置 ID')],
    obj: UpdateIntegrationAppsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if integration_apps.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该第三方应用集成配置')
    count = await integration_apps_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除第三方应用集成配置',
    dependencies=[DependsAgentJwtAuth],
    name='agent_delete_integration_apps',
)
async def agent_delete_integration_apps(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='第三方应用集成配置 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if integration_apps.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该第三方应用集成配置')
    from backend.app.integration.schema.integration_apps import DeleteIntegrationAppsParam
    count = await integration_apps_service.delete(db=db, obj=DeleteIntegrationAppsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
