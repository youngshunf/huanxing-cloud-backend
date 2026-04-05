"""HASN Owner API Key  - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.hasn.schema.hasn_owner_api_keys import (
    CreateHasnOwnerApiKeysParam,
    UpdateHasnOwnerApiKeysParam,
)
from backend.app.hasn.service.hasn_owner_api_keys_service import hasn_owner_api_keys_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='HASN Owner API Key 列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_hasn_owner_api_keyss(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await hasn_owner_api_keys_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建HASN Owner API Key ',
    dependencies=[DependsAgentAuth],
)
async def agent_create_hasn_owner_api_keys(
    db: CurrentSessionTransaction,
    obj: CreateHasnOwnerApiKeysParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await hasn_owner_api_keys_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN Owner API Key 详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_hasn_owner_api_keys(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Owner API Key  ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_owner_api_keys = await hasn_owner_api_keys_service.get(db=db, pk=pk)
    if hasn_owner_api_keys.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该HASN Owner API Key ')
    return response_base.success(data=hasn_owner_api_keys)


@router.put(
    '/{pk}',
    summary='更新HASN Owner API Key ',
    dependencies=[DependsAgentAuth],
)
async def agent_update_hasn_owner_api_keys(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Owner API Key  ID')],
    obj: UpdateHasnOwnerApiKeysParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_owner_api_keys = await hasn_owner_api_keys_service.get(db=db, pk=pk)
    if hasn_owner_api_keys.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Owner API Key ')
    count = await hasn_owner_api_keys_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN Owner API Key ',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_hasn_owner_api_keys(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Owner API Key  ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_owner_api_keys = await hasn_owner_api_keys_service.get(db=db, pk=pk)
    if hasn_owner_api_keys.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Owner API Key ')
    from backend.app.hasn.schema.hasn_owner_api_keys import DeleteHasnOwnerApiKeysParam
    count = await hasn_owner_api_keys_service.delete(db=db, obj=DeleteHasnOwnerApiKeysParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
