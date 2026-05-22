from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_posts import (
    CreateHasnPostsParam,
    DeleteHasnPostsParam,
    GetHasnPostsDetail,
    UpdateHasnPostsParam,
)
from backend.app.hasn.service.hasn_posts_service import hasn_posts_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取社区帖子详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_posts')
async def get_hasn_posts(
    db: CurrentSession, pk: Annotated[int, Path(description='社区帖子 ID')]
) -> ResponseSchemaModel[GetHasnPostsDetail]:
    hasn_posts = await hasn_posts_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_posts)


@router.get(
    '',
    summary='分页获取所有社区帖子',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_posts_paginated',
)
async def get_hasn_posts_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnPostsDetail]]:
    page_data = await hasn_posts_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区帖子',
    dependencies=[
        Depends(RequestPermission('hasn:posts:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_posts',
)
async def create_hasn_posts(db: CurrentSessionTransaction, obj: CreateHasnPostsParam) -> ResponseModel:
    await hasn_posts_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新社区帖子',
    dependencies=[
        Depends(RequestPermission('hasn:posts:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_posts',
)
async def update_hasn_posts(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='社区帖子 ID')], obj: UpdateHasnPostsParam
) -> ResponseModel:
    count = await hasn_posts_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除社区帖子',
    dependencies=[
        Depends(RequestPermission('hasn:posts:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_posts',
)
async def delete_hasn_posts(db: CurrentSessionTransaction, obj: DeleteHasnPostsParam) -> ResponseModel:
    count = await hasn_posts_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
