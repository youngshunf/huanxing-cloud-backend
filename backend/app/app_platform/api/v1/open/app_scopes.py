"""应用权限定义表（{domain}.* namespace） - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_scopes import GetAppScopesDetail
from backend.app.app_platform.service.app_scopes_service import app_scopes_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取应用权限定义表（{domain}.* namespace）列表',
    dependencies=[DependsPagination],
 name='open_get_app_scopess')
async def get_app_scopess(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppScopesDetail]]:
    page_data = await app_scopes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取应用权限定义表（{domain}.* namespace）详情',
 name='open_get_app_scopes')
async def get_app_scopes(
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')],
) -> ResponseSchemaModel[GetAppScopesDetail]:
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    return response_base.success(data=app_scopes)
