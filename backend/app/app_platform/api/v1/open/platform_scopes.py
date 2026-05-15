"""平台权限定义表（hasn.* namespace） - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.platform_scopes import GetPlatformScopesDetail
from backend.app.app_platform.service.platform_scopes_service import platform_scopes_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取平台权限定义表（hasn.* namespace）列表',
    dependencies=[DependsPagination],
 name='open_get_platform_scopess')
async def get_platform_scopess(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetPlatformScopesDetail]]:
    page_data = await platform_scopes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取平台权限定义表（hasn.* namespace）详情',
    name='open_get_platform_scopes',
)
async def get_platform_scopes(
    db: CurrentSession,
    pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')],
) -> ResponseSchemaModel[GetPlatformScopesDetail]:
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    return response_base.success(data=platform_scopes)
