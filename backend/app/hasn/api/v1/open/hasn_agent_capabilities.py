"""HASN Agent 能力声明 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_agent_capabilities import GetHasnAgentCapabilitiesDetail
from backend.app.hasn.service.hasn_agent_capabilities_service import hasn_agent_capabilities_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN Agent 能力声明列表',
    dependencies=[DependsPagination],
)
async def open_get_hasn_agent_capabilitiess(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnAgentCapabilitiesDetail]]:
    page_data = await hasn_agent_capabilities_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN Agent 能力声明详情',
)
async def open_get_hasn_agent_capabilities(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Agent 能力声明 ID')],
) -> ResponseSchemaModel[GetHasnAgentCapabilitiesDetail]:
    hasn_agent_capabilities = await hasn_agent_capabilities_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_agent_capabilities)
