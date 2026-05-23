"""社区收藏项 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_collection_items import GetHasnCollectionItemsDetail
from backend.app.hasn.service.hasn_collection_items_service import hasn_collection_items_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取社区收藏项列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_collection_items',
)
async def get_hasn_collection_items(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnCollectionItemsDetail]]:
    page_data = await hasn_collection_items_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取社区收藏项详情',
    name='open_get_hasn_collection_items_detail',
)
async def get_hasn_collection_items_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区收藏项 ID')],
) -> ResponseSchemaModel[GetHasnCollectionItemsDetail]:
    hasn_collection_items = await hasn_collection_items_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_collection_items)
