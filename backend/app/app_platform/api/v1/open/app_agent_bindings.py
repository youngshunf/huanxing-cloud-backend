"""Installation 绑定的 Agent 列 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_agent_bindings import GetAppAgentBindingsDetail
from backend.app.app_platform.service.app_agent_bindings_service import app_agent_bindings_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取Installation 绑定的 Agent 列列表',
    dependencies=[DependsPagination],
 name='open_get_app_agent_bindingss')
async def get_app_agent_bindingss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppAgentBindingsDetail]]:
    page_data = await app_agent_bindings_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取Installation 绑定的 Agent 列详情',
 name='open_get_app_agent_bindings')
async def get_app_agent_bindings(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')],
) -> ResponseSchemaModel[GetAppAgentBindingsDetail]:
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    return response_base.success(data=app_agent_bindings)
