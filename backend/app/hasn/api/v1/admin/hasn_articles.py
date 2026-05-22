from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_articles import (
    CreateHasnArticlesParam,
    DeleteHasnArticlesParam,
    GetHasnArticlesDetail,
    UpdateHasnArticlesParam,
)
from backend.app.hasn.service.hasn_articles_service import hasn_articles_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取社区文章详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_articles')
async def get_hasn_articles(
    db: CurrentSession, pk: Annotated[int, Path(description='社区文章 ID')]
) -> ResponseSchemaModel[GetHasnArticlesDetail]:
    hasn_articles = await hasn_articles_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_articles)


@router.get(
    '',
    summary='分页获取所有社区文章',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_articles_paginated',
)
async def get_hasn_articles_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnArticlesDetail]]:
    page_data = await hasn_articles_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区文章',
    dependencies=[
        Depends(RequestPermission('hasn:articles:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_articles',
)
async def create_hasn_articles(db: CurrentSessionTransaction, obj: CreateHasnArticlesParam) -> ResponseModel:
    await hasn_articles_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新社区文章',
    dependencies=[
        Depends(RequestPermission('hasn:articles:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_articles',
)
async def update_hasn_articles(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='社区文章 ID')], obj: UpdateHasnArticlesParam
) -> ResponseModel:
    count = await hasn_articles_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除社区文章',
    dependencies=[
        Depends(RequestPermission('hasn:articles:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_articles',
)
async def delete_hasn_articles(db: CurrentSessionTransaction, obj: DeleteHasnArticlesParam) -> ResponseModel:
    count = await hasn_articles_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
