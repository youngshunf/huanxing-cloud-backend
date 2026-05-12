"""HASN Agent  - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_agents import (
    AgentSyncRequest,
    AgentSyncResponse,
    CloudCreateAgentRequest,
    CloudCreateAgentResponse,
    CreateHasnAgentsParam,
    GetHasnAgentsDetail,
    UpdateHasnAgentsParam,
)
from backend.app.hasn.service.hasn_agents_service import agent_profile_service, hasn_agents_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '/sync',
    summary='同步云端 HASN Agent Profile 快照',
    dependencies=[DependsJwtAuth],
)
async def sync_my_hasn_agents(
    request: Request,
    db: CurrentSession,
    owner_id: str,
    after_revision: int | None = None,
) -> ResponseSchemaModel[AgentSyncResponse]:
    result = await agent_profile_service.sync_agents(
        db=db,
        request=AgentSyncRequest(owner_id=owner_id, after_revision=after_revision),
        user_id=request.user.id,
    )
    return response_base.success(data=result)


@router.post(
    '/cloud-create',
    summary='云端优先创建 HASN Agent Profile',
    dependencies=[DependsJwtAuth],
)
async def cloud_create_my_hasn_agent(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CloudCreateAgentRequest,
) -> ResponseSchemaModel[CloudCreateAgentResponse]:
    result = await agent_profile_service.create_cloud_first(db=db, request=obj, user_id=request.user.id)
    return response_base.success(data=result)


@router.get(
    '',
    summary='获取我的HASN Agent 列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_hasn_agentss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnAgentsDetail]]:
    user_id = request.user.id
    page_data = await hasn_agents_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN Agent ',
    dependencies=[DependsJwtAuth],
)
async def create_my_hasn_agents(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnAgentsParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await hasn_agents_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN Agent 详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_hasn_agents(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
) -> ResponseSchemaModel[GetHasnAgentsDetail]:
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该HASN Agent ')
    return response_base.success(data=hasn_agents)


@router.put(
    '/{pk}',
    summary='更新HASN Agent ',
    dependencies=[DependsJwtAuth],
)
async def update_my_hasn_agents(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
    obj: UpdateHasnAgentsParam,
) -> ResponseModel:
    user_id = request.user.id
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Agent ')
    count = await hasn_agents_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN Agent ',
    dependencies=[DependsJwtAuth],
)
async def delete_my_hasn_agents(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Agent ')
    from backend.app.hasn.schema.hasn_agents import DeleteHasnAgentsParam
    count = await hasn_agents_service.delete(db=db, obj=DeleteHasnAgentsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
