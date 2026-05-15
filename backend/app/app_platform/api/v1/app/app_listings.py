"""应用市场列表 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_listings import (
    CreateAppListingsParam,
    GetAppListingsDetail,
    UpdateAppListingsParam,
)
from backend.app.app_platform.service.app_listings_service import app_listings_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的应用市场列表列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_listingss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppListingsDetail]]:
    page_data = await app_listings_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用市场列表',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_listings(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppListingsParam,
) -> ResponseModel:
    result = await app_listings_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取应用市场列表详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_listings(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
) -> ResponseSchemaModel[GetAppListingsDetail]:
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该应用市场列表')
    return response_base.success(data=app_listings)


@router.put(
    '/{pk}',
    summary='更新应用市场列表',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_listings(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
    obj: UpdateAppListingsParam,
) -> ResponseModel:
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if getattr(app_listings, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该应用市场列表')
    count = await app_listings_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除应用市场列表',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_listings(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_listings = await app_listings_service.get(db=db, pk=pk)
    if app_listings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用市场列表')
    from backend.app.app_platform.schema.app_listings import DeleteAppListingsParam
    count = await app_listings_service.delete(db=db, obj=DeleteAppListingsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
