"""HASN Agent  - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_agents import GetHasnAgentsDetail
from backend.app.hasn.service.hasn_agents_service import hasn_agents_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN Agent 列表',
    dependencies=[DependsPagination],
)
async def open_get_hasn_agentss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnAgentsDetail]]:
    page_data = await hasn_agents_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN Agent 详情',
)
async def open_get_hasn_agents(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
) -> ResponseSchemaModel[GetHasnAgentsDetail]:
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_agents)
