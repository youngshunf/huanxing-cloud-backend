"""App 审核记录 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_reviews import GetAppReviewsDetail
from backend.app.app_platform.service.app_reviews_service import app_reviews_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App 审核记录列表',
    dependencies=[DependsPagination],
 name='open_get_app_reviewss')
async def get_app_reviewss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppReviewsDetail]]:
    page_data = await app_reviews_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App 审核记录详情',
 name='open_get_app_reviews')
async def get_app_reviews(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 审核记录 ID')],
) -> ResponseSchemaModel[GetAppReviewsDetail]:
    app_reviews = await app_reviews_service.get(db=db, pk=pk)
    return response_base.success(data=app_reviews)
