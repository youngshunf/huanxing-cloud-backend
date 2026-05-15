from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_resources import (
    CreateAppResourcesParam,
    DeleteAppResourcesParam,
    GetAppResourcesDetail,
    UpdateAppResourcesParam,
)
from backend.app.app_platform.service.app_resources_service import app_resources_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App Resource 定义详情', dependencies=[DependsJwtAuth], name='admin_get_app_resources')
async def get_app_resources(
    db: CurrentSession, pk: Annotated[int, Path(description='App Resource 定义 ID')]
) -> ResponseSchemaModel[GetAppResourcesDetail]:
    app_resources = await app_resources_service.get(db=db, pk=pk)
    return response_base.success(data=app_resources)


@router.get(
    '',
    summary='分页获取所有App Resource 定义',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_resourcess_paginated')
async def get_app_resourcess_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppResourcesDetail]]:
    page_data = await app_resources_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App Resource 定义',
    dependencies=[
        Depends(RequestPermission('app:resources:add')),
        DependsRBAC,
    ],
)
async def create_app_resources(db: CurrentSessionTransaction, obj: CreateAppResourcesParam) -> ResponseModel:
    await app_resources_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App Resource 定义',
    dependencies=[
        Depends(RequestPermission('app:resources:edit')),
        DependsRBAC,
    ],
)
async def update_app_resources(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App Resource 定义 ID')], obj: UpdateAppResourcesParam
) -> ResponseModel:
    count = await app_resources_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App Resource 定义',
    dependencies=[
        Depends(RequestPermission('app:resources:del')),
        DependsRBAC,
    ],
)
async def delete_app_resourcess(db: CurrentSessionTransaction, obj: DeleteAppResourcesParam) -> ResponseModel:
    count = await app_resources_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
