"""社区点赞 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_likes import GetHasnLikesDetail
from backend.app.hasn.service.hasn_likes_service import hasn_likes_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取社区点赞列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_likes',
)
async def get_hasn_likes(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnLikesDetail]]:
    page_data = await hasn_likes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取社区点赞详情',
    name='open_get_hasn_likes_detail',
)
async def get_hasn_likes_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区点赞 ID')],
) -> ResponseSchemaModel[GetHasnLikesDetail]:
    hasn_likes = await hasn_likes_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_likes)
