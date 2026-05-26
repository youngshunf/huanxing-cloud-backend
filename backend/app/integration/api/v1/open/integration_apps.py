"""第三方应用集成配置 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.integration.schema.integration_apps import GetIntegrationAppsDetail
from backend.app.integration.service.integration_apps_service import integration_apps_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取第三方应用集成配置列表',
    dependencies=[DependsPagination],
    name='open_get_integration_apps',
)
async def get_integration_apps(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetIntegrationAppsDetail]]:
    page_data = await integration_apps_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取第三方应用集成配置详情',
    name='open_get_integration_apps_detail',
)
async def get_integration_apps_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='第三方应用集成配置 ID')],
) -> ResponseSchemaModel[GetIntegrationAppsDetail]:
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    return response_base.success(data=integration_apps)
