from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_reviews import (
    CreateAppReviewsParam,
    DeleteAppReviewsParam,
    GetAppReviewsDetail,
    UpdateAppReviewsParam,
)
from backend.app.app_platform.service.app_reviews_service import app_reviews_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App 审核记录详情', dependencies=[DependsJwtAuth], name='admin_get_app_reviews')
async def get_app_reviews(
    db: CurrentSession, pk: Annotated[int, Path(description='App 审核记录 ID')]
) -> ResponseSchemaModel[GetAppReviewsDetail]:
    app_reviews = await app_reviews_service.get(db=db, pk=pk)
    return response_base.success(data=app_reviews)


@router.get(
    '',
    summary='分页获取所有App 审核记录',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_reviewss_paginated')
async def get_app_reviewss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppReviewsDetail]]:
    page_data = await app_reviews_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 审核记录',
    dependencies=[
        Depends(RequestPermission('app:reviews:add')),
        DependsRBAC,
    ],
)
async def create_app_reviews(db: CurrentSessionTransaction, obj: CreateAppReviewsParam) -> ResponseModel:
    await app_reviews_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App 审核记录',
    dependencies=[
        Depends(RequestPermission('app:reviews:edit')),
        DependsRBAC,
    ],
)
async def update_app_reviews(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App 审核记录 ID')], obj: UpdateAppReviewsParam
) -> ResponseModel:
    count = await app_reviews_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App 审核记录',
    dependencies=[
        Depends(RequestPermission('app:reviews:del')),
        DependsRBAC,
    ],
)
async def delete_app_reviewss(db: CurrentSessionTransaction, obj: DeleteAppReviewsParam) -> ResponseModel:
    count = await app_reviews_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
