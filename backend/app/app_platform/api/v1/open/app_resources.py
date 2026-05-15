"""App Resource 定义 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_resources import GetAppResourcesDetail
from backend.app.app_platform.service.app_resources_service import app_resources_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App Resource 定义列表',
    dependencies=[DependsPagination],
 name='open_get_app_resourcess')
async def get_app_resourcess(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppResourcesDetail]]:
    page_data = await app_resources_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App Resource 定义详情',
 name='open_get_app_resources')
async def get_app_resources(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App Resource 定义 ID')],
) -> ResponseSchemaModel[GetAppResourcesDetail]:
    app_resources = await app_resources_service.get(db=db, pk=pk)
    return response_base.success(data=app_resources)
