"""HASN Node 主 - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.hasn.schema.hasn_nodes import (
    CreateHasnNodesParam,
    UpdateHasnNodesParam,
)
from backend.app.hasn.service.hasn_nodes_service import hasn_nodes_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='HASN Node 主列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_hasn_nodess(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await hasn_nodes_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建HASN Node 主',
    dependencies=[DependsAgentAuth],
)
async def agent_create_hasn_nodes(
    db: CurrentSessionTransaction,
    obj: CreateHasnNodesParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await hasn_nodes_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN Node 主详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_hasn_nodes(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Node 主 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_nodes = await hasn_nodes_service.get(db=db, pk=pk)
    if hasn_nodes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该HASN Node 主')
    return response_base.success(data=hasn_nodes)


@router.put(
    '/{pk}',
    summary='更新HASN Node 主',
    dependencies=[DependsAgentAuth],
)
async def agent_update_hasn_nodes(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Node 主 ID')],
    obj: UpdateHasnNodesParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_nodes = await hasn_nodes_service.get(db=db, pk=pk)
    if hasn_nodes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Node 主')
    count = await hasn_nodes_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN Node 主',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_hasn_nodes(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Node 主 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_nodes = await hasn_nodes_service.get(db=db, pk=pk)
    if hasn_nodes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Node 主')
    from backend.app.hasn.schema.hasn_nodes import DeleteHasnNodesParam
    count = await hasn_nodes_service.delete(db=db, obj=DeleteHasnNodesParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
