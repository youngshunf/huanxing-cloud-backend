"""社区收藏项 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_collection_items import (
    CreateHasnCollectionItemsParam,
    GetHasnCollectionItemsDetail,
    UpdateHasnCollectionItemsParam,
)
from backend.app.hasn.service.hasn_collection_items_service import hasn_collection_items_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的社区收藏项列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_hasn_collection_items_detail',
)
async def get_my_hasn_collection_items_detail(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnCollectionItemsDetail]]:
    page_data = await hasn_collection_items_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区收藏项',
    dependencies=[DependsJwtAuth],
    name='app_create_my_hasn_collection_items',
)
async def create_my_hasn_collection_items(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnCollectionItemsParam,
) -> ResponseModel:
    result = await hasn_collection_items_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取社区收藏项详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_hasn_collection_items',
)
async def get_my_hasn_collection_items(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区收藏项 ID')],
) -> ResponseSchemaModel[GetHasnCollectionItemsDetail]:
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    if hasn_collection_items.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该社区收藏项')
    return response_base.success(data=hasn_collection_items)


@router.put(
    '/{pk}',
    summary='更新社区收藏项',
    dependencies=[DependsJwtAuth],
    name='app_update_my_hasn_collection_items',
)
async def update_my_hasn_collection_items(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区收藏项 ID')],
    obj: UpdateHasnCollectionItemsParam,
) -> ResponseModel:
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    if getattr(hasn_collection_items, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该社区收藏项')
    count = await hasn_collection_items_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除社区收藏项',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_hasn_collection_items',
)
async def delete_my_hasn_collection_items(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区收藏项 ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    if hasn_collection_items.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该社区收藏项')
    from backend.app.hasn.schema.hasn_collection_items import DeleteHasnCollectionItemsParam
    count = await hasn_collection_items_service.delete(db=db, obj=DeleteHasnCollectionItemsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
