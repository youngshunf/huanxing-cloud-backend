"""社区帖子 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_posts import GetHasnPostsDetail
from backend.app.hasn.service.hasn_posts_service import hasn_posts_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取社区帖子列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_posts',
)
async def get_hasn_posts(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnPostsDetail]]:
    page_data = await hasn_posts_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取社区帖子详情',
    name='open_get_hasn_posts_detail',
)
async def get_hasn_posts_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区帖子 ID')],
) -> ResponseSchemaModel[GetHasnPostsDetail]:
    hasn_posts = await hasn_posts_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_posts)
