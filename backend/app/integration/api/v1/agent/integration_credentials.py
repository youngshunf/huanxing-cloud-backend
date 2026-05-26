"""用户第三方应用凭证 - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.integration.schema.integration_credentials import (
    CreateIntegrationCredentialsParam,
    UpdateIntegrationCredentialsParam,
)
from backend.app.integration.service.integration_credentials_service import integration_credentials_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='用户第三方应用凭证列表',
    dependencies=[DependsAgentJwtAuth],
    name='agent_list_integration_credentials',
)
async def agent_list_integration_credentials(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await integration_credentials_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建用户第三方应用凭证',
    dependencies=[DependsAgentJwtAuth],
    name='agent_create_integration_credentials',
)
async def agent_create_integration_credentials(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateIntegrationCredentialsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await integration_credentials_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取用户第三方应用凭证详情',
    dependencies=[DependsAgentJwtAuth],
    name='agent_get_integration_credentials',
)
async def agent_get_integration_credentials(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='用户第三方应用凭证 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if integration_credentials.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该用户第三方应用凭证')
    return response_base.success(data=integration_credentials)


@router.put(
    '/{pk}',
    summary='更新用户第三方应用凭证',
    dependencies=[DependsAgentJwtAuth],
    name='agent_update_integration_credentials',
)
async def agent_update_integration_credentials(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='用户第三方应用凭证 ID')],
    obj: UpdateIntegrationCredentialsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if integration_credentials.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该用户第三方应用凭证')
    count = await integration_credentials_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除用户第三方应用凭证',
    dependencies=[DependsAgentJwtAuth],
    name='agent_delete_integration_credentials',
)
async def agent_delete_integration_credentials(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='用户第三方应用凭证 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if integration_credentials.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该用户第三方应用凭证')
    from backend.app.integration.schema.integration_credentials import DeleteIntegrationCredentialsParam
    count = await integration_credentials_service.delete(db=db, obj=DeleteIntegrationCredentialsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
