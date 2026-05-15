"""App 购买凭证 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_entitlements import GetAppEntitlementsDetail
from backend.app.app_platform.service.app_entitlements_service import app_entitlements_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App 购买凭证列表',
    dependencies=[DependsPagination],
 name='open_get_app_entitlementss')
async def get_app_entitlementss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppEntitlementsDetail]]:
    page_data = await app_entitlements_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App 购买凭证详情',
 name='open_get_app_entitlements')
async def get_app_entitlements(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 购买凭证 ID')],
) -> ResponseSchemaModel[GetAppEntitlementsDetail]:
    app_entitlements = await app_entitlements_service.get(db=db, pk=pk)
    return response_base.success(data=app_entitlements)
