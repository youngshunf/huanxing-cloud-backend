"""HASN 会话分层 - 逻辑会话 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_sessions import GetHasnSessionsDetail
from backend.app.hasn.service.hasn_sessions_service import hasn_sessions_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 会话分层 - 逻辑会话列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_sessions',
)
async def get_hasn_sessions(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnSessionsDetail]]:
    page_data = await hasn_sessions_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 会话分层 - 逻辑会话详情',
    name='open_get_hasn_sessions_detail',
)
async def get_hasn_sessions_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 会话分层 - 逻辑会话 ID')],
) -> ResponseSchemaModel[GetHasnSessionsDetail]:
    hasn_sessions = await hasn_sessions_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_sessions)
