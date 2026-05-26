"""第三方应用集成配置 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.integration.schema.integration_apps import (
    CreateIntegrationAppsParam,
    GetIntegrationAppsDetail,
    UpdateIntegrationAppsParam,
)
from backend.app.integration.service.integration_apps_service import integration_apps_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的第三方应用集成配置列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_integration_apps',
)
async def get_my_integration_apps(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetIntegrationAppsDetail]]:
    page_data = await integration_apps_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建第三方应用集成配置',
    dependencies=[DependsJwtAuth],
    name='app_create_my_integration_apps',
)
async def create_my_integration_apps(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateIntegrationAppsParam,
) -> ResponseModel:
    result = await integration_apps_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取第三方应用集成配置详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_integration_apps_detail',
)
async def get_my_integration_apps_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='第三方应用集成配置 ID')],
) -> ResponseSchemaModel[GetIntegrationAppsDetail]:
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    if integration_apps.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该第三方应用集成配置')
    return response_base.success(data=integration_apps)


@router.put(
    '/{pk}',
    summary='更新第三方应用集成配置',
    dependencies=[DependsJwtAuth],
    name='app_update_my_integration_apps',
)
async def update_my_integration_apps(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='第三方应用集成配置 ID')],
    obj: UpdateIntegrationAppsParam,
) -> ResponseModel:
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    if getattr(integration_apps, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该第三方应用集成配置')
    count = await integration_apps_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除第三方应用集成配置',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_integration_apps',
)
async def delete_my_integration_apps(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='第三方应用集成配置 ID')],
) -> ResponseModel:
    user_id = request.user.id
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    if integration_apps.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该第三方应用集成配置')
    from backend.app.integration.schema.integration_apps import DeleteIntegrationAppsParam
    count = await integration_apps_service.delete(db=db, obj=DeleteIntegrationAppsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
