"""HASN 群成员 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_group_members import GetHasnGroupMembersDetail
from backend.app.hasn.service.hasn_group_members_service import hasn_group_members_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 群成员列表',
    dependencies=[DependsPagination],
 name='open_open_get_hasn_group_memberss')
async def open_get_hasn_group_memberss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnGroupMembersDetail]]:
    page_data = await hasn_group_members_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 群成员详情',
 name='open_open_get_hasn_group_members')
async def open_get_hasn_group_members(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 群成员 ID')],
) -> ResponseSchemaModel[GetHasnGroupMembersDetail]:
    hasn_group_members = await hasn_group_members_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_group_members)
