from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_collections import (
    CreateHasnCollectionsParam,
    DeleteHasnCollectionsParam,
    GetHasnCollectionsDetail,
    UpdateHasnCollectionsParam,
)
from backend.app.hasn.service.hasn_collections_service import hasn_collections_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取社区收藏夹详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_collections')
async def get_hasn_collections(
    db: CurrentSession, pk: Annotated[int, Path(description='社区收藏夹 ID')]
) -> ResponseSchemaModel[GetHasnCollectionsDetail]:
    hasn_collections = await hasn_collections_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_collections)


@router.get(
    '',
    summary='分页获取所有社区收藏夹',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_collections_paginated',
)
async def get_hasn_collections_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnCollectionsDetail]]:
    page_data = await hasn_collections_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区收藏夹',
    dependencies=[
        Depends(RequestPermission('hasn:collections:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_collections',
)
async def create_hasn_collections(db: CurrentSessionTransaction, obj: CreateHasnCollectionsParam) -> ResponseModel:
    await hasn_collections_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新社区收藏夹',
    dependencies=[
        Depends(RequestPermission('hasn:collections:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_collections',
)
async def update_hasn_collections(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='社区收藏夹 ID')], obj: UpdateHasnCollectionsParam
) -> ResponseModel:
    count = await hasn_collections_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除社区收藏夹',
    dependencies=[
        Depends(RequestPermission('hasn:collections:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_collections',
)
async def delete_hasn_collections(db: CurrentSessionTransaction, obj: DeleteHasnCollectionsParam) -> ResponseModel:
    count = await hasn_collections_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
