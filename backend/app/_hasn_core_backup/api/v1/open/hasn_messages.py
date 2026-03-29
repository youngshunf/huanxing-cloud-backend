"""HASN 消息 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn_core.schema.hasn_messages import GetHasnMessagesDetail
from backend.app.hasn_core.service.hasn_messages_service import hasn_messages_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 消息列表',
    dependencies=[DependsPagination],
)
async def get_hasn_messagess(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnMessagesDetail]]:
    page_data = await hasn_messages_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 消息详情',
)
async def open_get_hasn_messages(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 消息 ID')],
) -> ResponseSchemaModel[GetHasnMessagesDetail]:
    hasn_messages = await hasn_messages_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_messages)
