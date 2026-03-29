"""HASN 未读计数 - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.hasn_core.schema.hasn_unread_counts import (
    CreateHasnUnreadCountsParam,
    UpdateHasnUnreadCountsParam,
)
from backend.app.hasn_core.service.hasn_unread_counts_service import hasn_unread_counts_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='HASN 未读计数列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_hasn_unread_countss(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await hasn_unread_counts_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建HASN 未读计数',
    dependencies=[DependsAgentAuth],
)
async def agent_create_hasn_unread_counts(
    db: CurrentSessionTransaction,
    obj: CreateHasnUnreadCountsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await hasn_unread_counts_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN 未读计数详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_hasn_unread_counts(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 未读计数 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_unread_counts = await hasn_unread_counts_service.get(db=db, pk=pk)
    if hasn_unread_counts.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该HASN 未读计数')
    return response_base.success(data=hasn_unread_counts)


@router.put(
    '/{pk}',
    summary='更新HASN 未读计数',
    dependencies=[DependsAgentAuth],
)
async def agent_update_hasn_unread_counts(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 未读计数 ID')],
    obj: UpdateHasnUnreadCountsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_unread_counts = await hasn_unread_counts_service.get(db=db, pk=pk)
    if hasn_unread_counts.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN 未读计数')
    count = await hasn_unread_counts_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN 未读计数',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_hasn_unread_counts(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 未读计数 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_unread_counts = await hasn_unread_counts_service.get(db=db, pk=pk)
    if hasn_unread_counts.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN 未读计数')
    from backend.app.hasn_core.schema.hasn_unread_counts import DeleteHasnUnreadCountsParam
    count = await hasn_unread_counts_service.delete(db=db, obj=DeleteHasnUnreadCountsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
