"""HASN 通知队列 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_notifications import GetHasnNotificationsDetail
from backend.app.hasn.service.hasn_notifications_service import hasn_notifications_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 通知队列列表',
    dependencies=[DependsPagination],
)
async def open_get_hasn_notificationss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnNotificationsDetail]]:
    page_data = await hasn_notifications_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 通知队列详情',
)
async def open_get_hasn_notifications(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 通知队列 ID')],
) -> ResponseSchemaModel[GetHasnNotificationsDetail]:
    hasn_notifications = await hasn_notifications_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_notifications)
