"""应用市场列表 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_listings import GetAppListingsDetail
from backend.app.app_platform.service.app_listings_service import app_listings_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取应用市场列表列表',
    dependencies=[DependsPagination],
 name='open_get_app_listingss')
async def get_app_listingss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppListingsDetail]]:
    page_data = await app_listings_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取应用市场列表详情',
 name='open_get_app_listings')
async def get_app_listings(
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用市场列表 ID')],
) -> ResponseSchemaModel[GetAppListingsDetail]:
    app_listings = await app_listings_service.get(db=db, pk=pk)
    return response_base.success(data=app_listings)
