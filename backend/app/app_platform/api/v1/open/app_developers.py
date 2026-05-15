"""应用开发者 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_developers import GetAppDevelopersDetail
from backend.app.app_platform.service.app_developers_service import app_developers_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取应用开发者列表',
    dependencies=[DependsPagination],
 name='open_get_app_developerss')
async def get_app_developerss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppDevelopersDetail]]:
    page_data = await app_developers_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取应用开发者详情',
 name='open_get_app_developers')
async def get_app_developers(
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用开发者 ID')],
) -> ResponseSchemaModel[GetAppDevelopersDetail]:
    app_developers = await app_developers_service.get(db=db, pk=pk)
    return response_base.success(data=app_developers)
