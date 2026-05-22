from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_likes import (
    CreateHasnLikesParam,
    DeleteHasnLikesParam,
    GetHasnLikesDetail,
    UpdateHasnLikesParam,
)
from backend.app.hasn.service.hasn_likes_service import hasn_likes_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取社区点赞详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_likes')
async def get_hasn_likes(
    db: CurrentSession, pk: Annotated[int, Path(description='社区点赞 ID')]
) -> ResponseSchemaModel[GetHasnLikesDetail]:
    hasn_likes = await hasn_likes_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_likes)


@router.get(
    '',
    summary='分页获取所有社区点赞',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_likes_paginated',
)
async def get_hasn_likes_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnLikesDetail]]:
    page_data = await hasn_likes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区点赞',
    dependencies=[
        Depends(RequestPermission('hasn:likes:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_likes',
)
async def create_hasn_likes(db: CurrentSessionTransaction, obj: CreateHasnLikesParam) -> ResponseModel:
    await hasn_likes_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新社区点赞',
    dependencies=[
        Depends(RequestPermission('hasn:likes:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_likes',
)
async def update_hasn_likes(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='社区点赞 ID')], obj: UpdateHasnLikesParam
) -> ResponseModel:
    count = await hasn_likes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除社区点赞',
    dependencies=[
        Depends(RequestPermission('hasn:likes:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_likes',
)
async def delete_hasn_likes(db: CurrentSessionTransaction, obj: DeleteHasnLikesParam) -> ResponseModel:
    count = await hasn_likes_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
