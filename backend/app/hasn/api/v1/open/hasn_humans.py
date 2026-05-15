"""HASN 人类用户身份 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_humans import GetHasnHumansDetail
from backend.app.hasn.service.hasn_humans_service import hasn_humans_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 人类用户身份列表',
    dependencies=[DependsPagination],
 name='open_open_get_hasn_humanss')
async def open_get_hasn_humanss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnHumansDetail]]:
    page_data = await hasn_humans_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 人类用户身份详情',
 name='open_open_get_hasn_humans')
async def open_get_hasn_humans(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 人类用户身份 ID')],
) -> ResponseSchemaModel[GetHasnHumansDetail]:
    hasn_humans = await hasn_humans_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_humans)
