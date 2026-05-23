"""社区关注 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_follows import GetHasnFollowsDetail
from backend.app.hasn.service.hasn_follows_service import hasn_follows_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取社区关注列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_follows',
)
async def get_hasn_follows(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnFollowsDetail]]:
    page_data = await hasn_follows_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取社区关注详情',
    name='open_get_hasn_follows_detail',
)
async def get_hasn_follows_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区关注 ID')],
) -> ResponseSchemaModel[GetHasnFollowsDetail]:
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_follows)
