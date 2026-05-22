"""社区评论 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_comments import GetHasnCommentsDetail
from backend.app.hasn.service.hasn_comments_service import hasn_comments_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取社区评论列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_comments',
)
async def get_hasn_comments(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnCommentsDetail]]:
    page_data = await hasn_comments_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取社区评论详情',
    name='open_get_hasn_comments',
)
async def get_hasn_comments(
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区评论 ID')],
) -> ResponseSchemaModel[GetHasnCommentsDetail]:
    hasn_comments = await hasn_comments_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_comments)
