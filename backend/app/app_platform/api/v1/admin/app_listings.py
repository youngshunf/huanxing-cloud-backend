from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_listings import (
    CreateAppListingsParam,
    DeleteAppListingsParam,
    GetAppListingsDetail,
    UpdateAppListingsParam,
)
from backend.app.app_platform.service.app_listings_service import app_listings_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取应用市场列表详情', dependencies=[DependsJwtAuth], name='admin_get_app_listings')
async def get_app_listings(
    db: CurrentSession, pk: Annotated[int, Path(description='应用市场列表 ID')]
) -> ResponseSchemaModel[GetAppListingsDetail]:
    app_listings = await app_listings_service.get(db=db, pk=pk)
    return response_base.success(data=app_listings)


@router.get(
    '',
    summary='分页获取所有应用市场列表',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_listingss_paginated')
async def get_app_listingss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppListingsDetail]]:
    page_data = await app_listings_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用市场列表',
    dependencies=[
        Depends(RequestPermission('app:listings:add')),
        DependsRBAC,
    ],
)
async def create_app_listings(db: CurrentSessionTransaction, obj: CreateAppListingsParam) -> ResponseModel:
    await app_listings_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新应用市场列表',
    dependencies=[
        Depends(RequestPermission('app:listings:edit')),
        DependsRBAC,
    ],
)
async def update_app_listings(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='应用市场列表 ID')], obj: UpdateAppListingsParam
) -> ResponseModel:
    count = await app_listings_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除应用市场列表',
    dependencies=[
        Depends(RequestPermission('app:listings:del')),
        DependsRBAC,
    ],
)
async def delete_app_listingss(db: CurrentSessionTransaction, obj: DeleteAppListingsParam) -> ResponseModel:
    count = await app_listings_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
