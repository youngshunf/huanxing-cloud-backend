"""Valid deduplicated lead contact - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.lead_automation.schema.lead_contact import GetLeadContactDetail
from backend.app.lead_automation.service.lead_contact_service import lead_contact_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取Valid deduplicated lead contact列表',
    dependencies=[DependsPagination],
)
async def get_lead_contacts(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetLeadContactDetail]]:
    page_data = await lead_contact_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取Valid deduplicated lead contact详情',
)
async def get_lead_contact(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Valid deduplicated lead contact ID')],
) -> ResponseSchemaModel[GetLeadContactDetail]:
    lead_contact = await lead_contact_service.get(db=db, pk=pk)
    return response_base.success(data=lead_contact)
