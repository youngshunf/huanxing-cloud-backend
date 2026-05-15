"""App Event 定义 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_events import GetAppEventsDetail
from backend.app.app_platform.service.app_events_service import app_events_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App Event 定义列表',
    dependencies=[DependsPagination],
 name='open_get_app_eventss')
async def get_app_eventss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppEventsDetail]]:
    page_data = await app_events_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App Event 定义详情',
 name='open_get_app_events')
async def get_app_events(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App Event 定义 ID')],
) -> ResponseSchemaModel[GetAppEventsDetail]:
    app_events = await app_events_service.get(db=db, pk=pk)
    return response_base.success(data=app_events)
