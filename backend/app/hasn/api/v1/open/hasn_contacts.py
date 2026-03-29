"""HASN 联系人关系 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_contacts import GetHasnContactsDetail
from backend.app.hasn.service.hasn_contacts_service import hasn_contacts_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 联系人关系列表',
    dependencies=[DependsPagination],
)
async def open_get_hasn_contactss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnContactsDetail]]:
    page_data = await hasn_contacts_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 联系人关系详情',
)
async def open_get_hasn_contacts(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 联系人关系 ID')],
) -> ResponseSchemaModel[GetHasnContactsDetail]:
    hasn_contacts = await hasn_contacts_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_contacts)
