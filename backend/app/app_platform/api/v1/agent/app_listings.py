"""应用市场列表 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.app_platform.schema.app_listings import (
    CreateAppListingsParam,
    UpdateAppListingsParam,
)
from backend.app.app_platform.service.app_listings_service import app_listings_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='应用市场列表列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_listingss(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await app_listings_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建应用市场列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_listings(
    db: CurrentSessionTransaction,
    obj: CreateAppListingsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await app_listings_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取应用市场列表详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_listings(
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该应用市场列表')
    return response_base.success(data=app_listings)


@router.put(
    '/{pk}',
    summary='更新应用市场列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_listings(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
    obj: UpdateAppListingsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该应用市场列表')
    count = await app_listings_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除应用市场列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_listings(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用市场列表')
    from backend.app.app_platform.schema.app_listings import DeleteAppListingsParam
    count = await app_listings_service.delete(db=db, obj=DeleteAppListingsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
