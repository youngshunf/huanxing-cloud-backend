from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_permission_grants import (
    CreateAppPermissionGrantsParam,
    DeleteAppPermissionGrantsParam,
    GetAppPermissionGrantsDetail,
    UpdateAppPermissionGrantsParam,
)
from backend.app.app_platform.service.app_permission_grants_service import app_permission_grants_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取权限授予记录详情', dependencies=[DependsJwtAuth], name='admin_get_app_permission_grants')
async def get_app_permission_grants(
    db: CurrentSession, pk: Annotated[int, Path(description='权限授予记录 ID')]
) -> ResponseSchemaModel[GetAppPermissionGrantsDetail]:
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    return response_base.success(data=app_permission_grants)


@router.get(
    '',
    summary='分页获取所有权限授予记录',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_permission_grantss_paginated')
async def get_app_permission_grantss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppPermissionGrantsDetail]]:
    page_data = await app_permission_grants_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建权限授予记录',
    dependencies=[
        Depends(RequestPermission('app:permission:grants:add')),
        DependsRBAC,
    ],
)
async def create_app_permission_grants(db: CurrentSessionTransaction, obj: CreateAppPermissionGrantsParam) -> ResponseModel:
    await app_permission_grants_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新权限授予记录',
    dependencies=[
        Depends(RequestPermission('app:permission:grants:edit')),
        DependsRBAC,
    ],
)
async def update_app_permission_grants(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='权限授予记录 ID')], obj: UpdateAppPermissionGrantsParam
) -> ResponseModel:
    count = await app_permission_grants_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除权限授予记录',
    dependencies=[
        Depends(RequestPermission('app:permission:grants:del')),
        DependsRBAC,
    ],
)
async def delete_app_permission_grantss(db: CurrentSessionTransaction, obj: DeleteAppPermissionGrantsParam) -> ResponseModel:
    count = await app_permission_grants_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
