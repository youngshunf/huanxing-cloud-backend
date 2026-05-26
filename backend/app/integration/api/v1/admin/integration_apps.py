from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.integration.schema.integration_apps import (
    CreateIntegrationAppsParam,
    DeleteIntegrationAppsParam,
    GetIntegrationAppsDetail,
    UpdateIntegrationAppsParam,
)
from backend.app.integration.service.integration_apps_service import integration_apps_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取第三方应用集成配置详情', dependencies=[DependsJwtAuth], name='admin_get_integration_apps')
async def get_integration_apps(
    db: CurrentSession, pk: Annotated[int, Path(description='第三方应用集成配置 ID')]
) -> ResponseSchemaModel[GetIntegrationAppsDetail]:
    integration_apps = await integration_apps_service.get(db=db, pk=pk)
    return response_base.success(data=integration_apps)


@router.get(
    '',
    summary='分页获取所有第三方应用集成配置',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_integration_apps_paginated',
)
async def get_integration_apps_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetIntegrationAppsDetail]]:
    page_data = await integration_apps_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建第三方应用集成配置',
    dependencies=[
        Depends(RequestPermission('integration:apps:add')),
        DependsRBAC,
    ],
    name='admin_create_integration_apps',
)
async def create_integration_apps(db: CurrentSessionTransaction, obj: CreateIntegrationAppsParam) -> ResponseModel:
    await integration_apps_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新第三方应用集成配置',
    dependencies=[
        Depends(RequestPermission('integration:apps:edit')),
        DependsRBAC,
    ],
    name='admin_update_integration_apps',
)
async def update_integration_apps(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='第三方应用集成配置 ID')], obj: UpdateIntegrationAppsParam
) -> ResponseModel:
    count = await integration_apps_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除第三方应用集成配置',
    dependencies=[
        Depends(RequestPermission('integration:apps:del')),
        DependsRBAC,
    ],
    name='admin_delete_integration_apps',
)
async def delete_integration_apps(db: CurrentSessionTransaction, obj: DeleteIntegrationAppsParam) -> ResponseModel:
    count = await integration_apps_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
