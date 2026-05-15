"""App Tool 定义 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_tools import GetAppToolsDetail
from backend.app.app_platform.service.app_tools_service import app_tools_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App Tool 定义列表',
    dependencies=[DependsPagination],
 name='open_get_app_toolss')
async def get_app_toolss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppToolsDetail]]:
    page_data = await app_tools_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App Tool 定义详情',
 name='open_get_app_tools')
async def get_app_tools(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App Tool 定义 ID')],
) -> ResponseSchemaModel[GetAppToolsDetail]:
    app_tools = await app_tools_service.get(db=db, pk=pk)
    return response_base.success(data=app_tools)
