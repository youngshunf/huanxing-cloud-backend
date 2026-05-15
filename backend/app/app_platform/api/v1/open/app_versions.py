"""App 版本 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_versions import GetAppVersionsDetail
from backend.app.app_platform.service.app_versions_service import app_versions_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App 版本列表',
    dependencies=[DependsPagination],
 name='open_get_app_versionss')
async def get_app_versionss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppVersionsDetail]]:
    page_data = await app_versions_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App 版本详情',
    name='open_get_app_versions',
)
async def get_app_versions(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 版本 ID')],
) -> ResponseSchemaModel[GetAppVersionsDetail]:
    app_versions = await app_versions_service.get(db=db, pk=pk)
    return response_base.success(data=app_versions)
