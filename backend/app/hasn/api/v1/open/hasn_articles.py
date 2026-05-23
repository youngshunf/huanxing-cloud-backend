"""社区文章 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_articles import GetHasnArticlesDetail
from backend.app.hasn.service.hasn_articles_service import hasn_articles_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取社区文章列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_articles',
)
async def get_hasn_articles(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnArticlesDetail]]:
    page_data = await hasn_articles_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取社区文章详情',
    name='open_get_hasn_articles_detail',
)
async def get_hasn_articles_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区文章 ID')],
) -> ResponseSchemaModel[GetHasnArticlesDetail]:
    hasn_articles = await hasn_articles_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_articles)
