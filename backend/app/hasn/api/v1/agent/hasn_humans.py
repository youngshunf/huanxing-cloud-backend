"""HASN 人类用户身份 - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.hasn.schema.hasn_humans import (
    CreateHasnHumansParam,
    UpdateHasnHumansParam,
)
from backend.app.hasn.service.hasn_humans_service import hasn_humans_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='HASN 人类用户身份列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_hasn_humanss(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await hasn_humans_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建HASN 人类用户身份',
    dependencies=[DependsAgentAuth],
)
async def agent_create_hasn_humans(
    db: CurrentSessionTransaction,
    obj: CreateHasnHumansParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await hasn_humans_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN 人类用户身份详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_hasn_humans(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 人类用户身份 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_humans = await hasn_humans_service.get(db=db, pk=pk)
    if hasn_humans.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该HASN 人类用户身份')
    return response_base.success(data=hasn_humans)


@router.put(
    '/{pk}',
    summary='更新HASN 人类用户身份',
    dependencies=[DependsAgentAuth],
)
async def agent_update_hasn_humans(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 人类用户身份 ID')],
    obj: UpdateHasnHumansParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_humans = await hasn_humans_service.get(db=db, pk=pk)
    if hasn_humans.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN 人类用户身份')
    count = await hasn_humans_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN 人类用户身份',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_hasn_humans(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 人类用户身份 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_humans = await hasn_humans_service.get(db=db, pk=pk)
    if hasn_humans.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN 人类用户身份')
    from backend.app.hasn.schema.hasn_humans import DeleteHasnHumansParam
    count = await hasn_humans_service.delete(db=db, obj=DeleteHasnHumansParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
