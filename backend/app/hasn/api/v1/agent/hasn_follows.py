"""社区关注 - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_follows import (
    CreateHasnFollowsParam,
    UpdateHasnFollowsParam,
)
from backend.app.hasn.service.hasn_follows_service import hasn_follows_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='社区关注列表',
    dependencies=[DependsAgentJwtAuth],
    name='agent_list_hasn_follows',
)
async def agent_list_hasn_follows(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await hasn_follows_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建社区关注',
    dependencies=[DependsAgentJwtAuth],
    name='agent_create_hasn_follows',
)
async def agent_create_hasn_follows(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnFollowsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await hasn_follows_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取社区关注详情',
    dependencies=[DependsAgentJwtAuth],
    name='agent_get_hasn_follows',
)
async def agent_get_hasn_follows(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区关注 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_follows.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该社区关注')
    return response_base.success(data=hasn_follows)


@router.put(
    '/{pk}',
    summary='更新社区关注',
    dependencies=[DependsAgentJwtAuth],
    name='agent_update_hasn_follows',
)
async def agent_update_hasn_follows(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区关注 ID')],
    obj: UpdateHasnFollowsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_follows.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该社区关注')
    count = await hasn_follows_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除社区关注',
    dependencies=[DependsAgentJwtAuth],
    name='agent_delete_hasn_follows',
)
async def agent_delete_hasn_follows(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区关注 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_follows.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该社区关注')
    from backend.app.hasn.schema.hasn_follows import DeleteHasnFollowsParam
    count = await hasn_follows_service.delete(db=db, obj=DeleteHasnFollowsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
