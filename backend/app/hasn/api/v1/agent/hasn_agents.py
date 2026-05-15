"""HASN Agent  - Agent API

认证方式: Agent JWT (DependsAgentJwtAuth)
Agent 信息: 通过 request.state.agent 获取 AgentTokenPayload
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_agents import (
    CreateHasnAgentsParam,
    UpdateHasnAgentsParam,
)
from backend.app.hasn.service.hasn_agents_service import hasn_agents_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.dataclasses import AgentTokenPayload
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()

@router.get(
    '',
    summary='HASN Agent 列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_hasn_agentss(
    db: CurrentSession,
    request: Request) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    data = await hasn_agents_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=data)

@router.post(
    '',
    summary='创建HASN Agent ',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_hasn_agents(
    db: CurrentSessionTransaction,
    request: Request,
    obj: CreateHasnAgentsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    result = await hasn_agents_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)

@router.get(
    '/{pk}',
    summary='获取HASN Agent 详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_hasn_agents(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='HASN Agent  ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该HASN Agent ')
    return response_base.success(data=hasn_agents)

@router.put(
    '/{pk}',
    summary='更新HASN Agent ',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_hasn_agents(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
    obj: UpdateHasnAgentsParam) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Agent ')
    count = await hasn_agents_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()

@router.delete(
    '/{pk}',
    summary='删除HASN Agent ',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_hasn_agents(
    db: CurrentSession,
    request: Request,
    pk: Annotated[int, Path(description='HASN Agent  ID')]) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent

    user_id = agent.owner_user_id
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Agent ')
    from backend.app.hasn.schema.hasn_agents import DeleteHasnAgentsParam
    count = await hasn_agents_service.delete(db=db, obj=DeleteHasnAgentsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
