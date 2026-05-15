"""权限授予记录 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_permission_grants import GetAppPermissionGrantsDetail
from backend.app.app_platform.service.app_permission_grants_service import app_permission_grants_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取权限授予记录列表',
    dependencies=[DependsPagination],
 name='open_get_app_permission_grantss')
async def get_app_permission_grantss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppPermissionGrantsDetail]]:
    page_data = await app_permission_grants_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取权限授予记录详情',
 name='open_get_app_permission_grants')
async def get_app_permission_grants(
    db: CurrentSession,
    pk: Annotated[int, Path(description='权限授予记录 ID')],
) -> ResponseSchemaModel[GetAppPermissionGrantsDetail]:
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    return response_base.success(data=app_permission_grants)
