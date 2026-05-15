"""HASN 会话 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_conversations import GetHasnConversationsDetail
from backend.app.hasn.service.hasn_conversations_service import hasn_conversations_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 会话列表',
    dependencies=[DependsPagination],
 name='open_open_get_hasn_conversationss')
async def open_get_hasn_conversationss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnConversationsDetail]]:
    page_data = await hasn_conversations_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 会话详情',
 name='open_open_get_hasn_conversations')
async def open_get_hasn_conversations(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 会话 ID')],
) -> ResponseSchemaModel[GetHasnConversationsDetail]:
    hasn_conversations = await hasn_conversations_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_conversations)
