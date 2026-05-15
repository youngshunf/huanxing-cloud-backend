"""App 清单 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_manifests import GetAppManifestsDetail
from backend.app.app_platform.service.app_manifests_service import app_manifests_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App 清单列表',
    dependencies=[DependsPagination],
 name='open_get_app_manifestss')
async def get_app_manifestss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppManifestsDetail]]:
    page_data = await app_manifests_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App 清单详情',
 name='open_get_app_manifests')
async def get_app_manifests(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 清单 ID')],
) -> ResponseSchemaModel[GetAppManifestsDetail]:
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    return response_base.success(data=app_manifests)
