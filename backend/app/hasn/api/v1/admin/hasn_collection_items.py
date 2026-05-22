from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_collection_items import (
    CreateHasnCollectionItemsParam,
    DeleteHasnCollectionItemsParam,
    GetHasnCollectionItemsDetail,
    UpdateHasnCollectionItemsParam,
)
from backend.app.hasn.service.hasn_collection_items_service import hasn_collection_items_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取社区收藏项详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_collection_items')
async def get_hasn_collection_items(
    db: CurrentSession, pk: Annotated[int, Path(description='社区收藏项 ID')]
) -> ResponseSchemaModel[GetHasnCollectionItemsDetail]:
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_collection_items)


@router.get(
    '',
    summary='分页获取所有社区收藏项',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_collection_items_paginated',
)
async def get_hasn_collection_items_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnCollectionItemsDetail]]:
    page_data = await hasn_collection_items_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区收藏项',
    dependencies=[
        Depends(RequestPermission('hasn:collection:items:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_collection_items',
)
async def create_hasn_collection_items(db: CurrentSessionTransaction, obj: CreateHasnCollectionItemsParam) -> ResponseModel:
    await hasn_collection_items_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新社区收藏项',
    dependencies=[
        Depends(RequestPermission('hasn:collection:items:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_collection_items',
)
async def update_hasn_collection_items(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='社区收藏项 ID')], obj: UpdateHasnCollectionItemsParam
) -> ResponseModel:
    count = await hasn_collection_items_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除社区收藏项',
    dependencies=[
        Depends(RequestPermission('hasn:collection:items:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_collection_items',
)
async def delete_hasn_collection_items(db: CurrentSessionTransaction, obj: DeleteHasnCollectionItemsParam) -> ResponseModel:
    count = await hasn_collection_items_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
