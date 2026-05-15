"""HASN 未读计数 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_unread_counts import GetHasnUnreadCountsDetail
from backend.app.hasn.service.hasn_unread_counts_service import hasn_unread_counts_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 未读计数列表',
    dependencies=[DependsPagination],
 name='open_open_get_hasn_unread_countss')
async def open_get_hasn_unread_countss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnUnreadCountsDetail]]:
    page_data = await hasn_unread_counts_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 未读计数详情',
 name='open_open_get_hasn_unread_counts')
async def open_get_hasn_unread_counts(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 未读计数 ID')],
) -> ResponseSchemaModel[GetHasnUnreadCountsDetail]:
    hasn_unread_counts = await hasn_unread_counts_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_unread_counts)
