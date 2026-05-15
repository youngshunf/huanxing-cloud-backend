"""App 安装记录 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_installations import GetAppInstallationsDetail
from backend.app.app_platform.service.app_installations_service import app_installations_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取App 安装记录列表',
    dependencies=[DependsPagination],
 name='open_get_app_installationss')
async def get_app_installationss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppInstallationsDetail]]:
    page_data = await app_installations_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取App 安装记录详情',
 name='open_get_app_installations')
async def get_app_installations(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 安装记录 ID')],
) -> ResponseSchemaModel[GetAppInstallationsDetail]:
    app_installations = await app_installations_service.get(db=db, pk=pk)
    return response_base.success(data=app_installations)
