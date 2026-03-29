"""HASN 交易会话 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_trade_sessions import GetHasnTradeSessionsDetail
from backend.app.hasn.service.hasn_trade_sessions_service import hasn_trade_sessions_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 交易会话列表',
    dependencies=[DependsPagination],
)
async def open_get_hasn_trade_sessionss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnTradeSessionsDetail]]:
    page_data = await hasn_trade_sessions_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 交易会话详情',
)
async def open_get_hasn_trade_sessions(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 交易会话 ID')],
) -> ResponseSchemaModel[GetHasnTradeSessionsDetail]:
    hasn_trade_sessions = await hasn_trade_sessions_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_trade_sessions)
