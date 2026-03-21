"""HASN Agent - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 owner_id 限制为用户自己的 Agent
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_agents import (
    GetHasnAgentsDetail,
)
from backend.app.hasn.service.hasn_agents_service import hasn_agents_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取我的HASN Agent 列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_hasn_agents(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnAgentsDetail]]:
    page_data = await hasn_agents_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN Agent 详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_hasn_agents_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Agent ID')],
) -> ResponseSchemaModel[GetHasnAgentsDetail]:
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_agents)
