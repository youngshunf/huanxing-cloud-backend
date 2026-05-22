from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_comments import (
    CreateHasnCommentsParam,
    DeleteHasnCommentsParam,
    GetHasnCommentsDetail,
    UpdateHasnCommentsParam,
)
from backend.app.hasn.service.hasn_comments_service import hasn_comments_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取社区评论详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_comments')
async def get_hasn_comments(
    db: CurrentSession, pk: Annotated[int, Path(description='社区评论 ID')]
) -> ResponseSchemaModel[GetHasnCommentsDetail]:
    hasn_comments = await hasn_comments_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_comments)


@router.get(
    '',
    summary='分页获取所有社区评论',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_comments_paginated',
)
async def get_hasn_comments_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnCommentsDetail]]:
    page_data = await hasn_comments_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区评论',
    dependencies=[
        Depends(RequestPermission('hasn:comments:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_comments',
)
async def create_hasn_comments(db: CurrentSessionTransaction, obj: CreateHasnCommentsParam) -> ResponseModel:
    await hasn_comments_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新社区评论',
    dependencies=[
        Depends(RequestPermission('hasn:comments:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_comments',
)
async def update_hasn_comments(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='社区评论 ID')], obj: UpdateHasnCommentsParam
) -> ResponseModel:
    count = await hasn_comments_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除社区评论',
    dependencies=[
        Depends(RequestPermission('hasn:comments:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_comments',
)
async def delete_hasn_comments(db: CurrentSessionTransaction, obj: DeleteHasnCommentsParam) -> ResponseModel:
    count = await hasn_comments_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
