"""社区收藏夹 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_collections import GetHasnCollectionsDetail
from backend.app.hasn.service.hasn_collections_service import hasn_collections_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取社区收藏夹列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_collections',
)
async def get_hasn_collections(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnCollectionsDetail]]:
    page_data = await hasn_collections_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取社区收藏夹详情',
    name='open_get_hasn_collections',
)
async def get_hasn_collections(
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区收藏夹 ID')],
) -> ResponseSchemaModel[GetHasnCollectionsDetail]:
    hasn_collections = await hasn_collections_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_collections)
