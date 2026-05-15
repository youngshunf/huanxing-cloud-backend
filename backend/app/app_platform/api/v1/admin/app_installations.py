from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_installations import (
    CreateAppInstallationsParam,
    DeleteAppInstallationsParam,
    GetAppInstallationsDetail,
    UpdateAppInstallationsParam,
)
from backend.app.app_platform.service.app_installations_service import app_installations_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App 安装记录详情', dependencies=[DependsJwtAuth], name='admin_get_app_installations')
async def get_app_installations(
    db: CurrentSession, pk: Annotated[int, Path(description='App 安装记录 ID')]
) -> ResponseSchemaModel[GetAppInstallationsDetail]:
    app_installations = await app_installations_service.get(db=db, pk=pk)
    return response_base.success(data=app_installations)


@router.get(
    '',
    summary='分页获取所有App 安装记录',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_installationss_paginated')
async def get_app_installationss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppInstallationsDetail]]:
    page_data = await app_installations_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 安装记录',
    dependencies=[
        Depends(RequestPermission('app:installations:add')),
        DependsRBAC,
    ],
)
async def create_app_installations(db: CurrentSessionTransaction, obj: CreateAppInstallationsParam) -> ResponseModel:
    await app_installations_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App 安装记录',
    dependencies=[
        Depends(RequestPermission('app:installations:edit')),
        DependsRBAC,
    ],
)
async def update_app_installations(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App 安装记录 ID')], obj: UpdateAppInstallationsParam
) -> ResponseModel:
    count = await app_installations_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App 安装记录',
    dependencies=[
        Depends(RequestPermission('app:installations:del')),
        DependsRBAC,
    ],
)
async def delete_app_installationss(db: CurrentSessionTransaction, obj: DeleteAppInstallationsParam) -> ResponseModel:
    count = await app_installations_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
