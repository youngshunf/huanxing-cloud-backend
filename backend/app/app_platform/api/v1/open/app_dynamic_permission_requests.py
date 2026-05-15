"""动态权限请求 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_dynamic_permission_requests import GetAppDynamicPermissionRequestsDetail
from backend.app.app_platform.service.app_dynamic_permission_requests_service import app_dynamic_permission_requests_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取动态权限请求列表',
    dependencies=[DependsPagination],
 name='open_get_app_dynamic_permission_requestss')
async def get_app_dynamic_permission_requestss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppDynamicPermissionRequestsDetail]]:
    page_data = await app_dynamic_permission_requests_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取动态权限请求详情',
 name='open_get_app_dynamic_permission_requests')
async def get_app_dynamic_permission_requests(
    db: CurrentSession,
    pk: Annotated[int, Path(description='动态权限请求 ID')],
) -> ResponseSchemaModel[GetAppDynamicPermissionRequestsDetail]:
    app_dynamic_permission_requests = await app_dynamic_permission_requests_service.get(db=db, pk=pk)
    return response_base.success(data=app_dynamic_permission_requests)
