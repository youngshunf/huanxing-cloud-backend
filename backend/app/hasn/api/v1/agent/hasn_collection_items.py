"""社区收藏项 - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_collection_items import (
    CreateHasnCollectionItemsParam,
    UpdateHasnCollectionItemsParam,
)
from backend.app.hasn.service.hasn_collection_items_service import hasn_collection_items_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='社区收藏项列表',
    dependencies=[DependsAgentJwtAuth],
    name='agent_list_hasn_collection_items',
)
async def agent_list_hasn_collection_items(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await hasn_collection_items_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建社区收藏项',
    dependencies=[DependsAgentJwtAuth],
    name='agent_create_hasn_collection_items',
)
async def agent_create_hasn_collection_items(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnCollectionItemsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await hasn_collection_items_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取社区收藏项详情',
    dependencies=[DependsAgentJwtAuth],
    name='agent_get_hasn_collection_items',
)
async def agent_get_hasn_collection_items(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区收藏项 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_collection_items.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该社区收藏项')
    return response_base.success(data=hasn_collection_items)


@router.put(
    '/{pk}',
    summary='更新社区收藏项',
    dependencies=[DependsAgentJwtAuth],
    name='agent_update_hasn_collection_items',
)
async def agent_update_hasn_collection_items(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区收藏项 ID')],
    obj: UpdateHasnCollectionItemsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_collection_items.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该社区收藏项')
    count = await hasn_collection_items_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除社区收藏项',
    dependencies=[DependsAgentJwtAuth],
    name='agent_delete_hasn_collection_items',
)
async def agent_delete_hasn_collection_items(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区收藏项 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_collection_items.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该社区收藏项')
    from backend.app.hasn.schema.hasn_collection_items import DeleteHasnCollectionItemsParam
    count = await hasn_collection_items_service.delete(db=db, obj=DeleteHasnCollectionItemsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
