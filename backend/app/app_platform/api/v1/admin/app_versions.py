from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_versions import (
    CreateAppVersionsParam,
    DeleteAppVersionsParam,
    GetAppVersionsDetail,
    UpdateAppVersionsParam,
)
from backend.app.app_platform.service.app_versions_service import app_versions_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App 版本详情', dependencies=[DependsJwtAuth], name='admin_get_app_versions')
async def get_app_versions(
    db: CurrentSession, pk: Annotated[int, Path(description='App 版本 ID')]
) -> ResponseSchemaModel[GetAppVersionsDetail]:
    app_versions = await app_versions_service.get(db=db, pk=pk)
    return response_base.success(data=app_versions)


@router.get(
    '',
    summary='分页获取所有App 版本',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_versionss_paginated')
async def get_app_versionss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppVersionsDetail]]:
    page_data = await app_versions_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 版本',
    dependencies=[
        Depends(RequestPermission('app:versions:add')),
        DependsRBAC,
    ],
)
async def create_app_versions(db: CurrentSessionTransaction, obj: CreateAppVersionsParam) -> ResponseModel:
    await app_versions_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App 版本',
    dependencies=[
        Depends(RequestPermission('app:versions:edit')),
        DependsRBAC,
    ],
)
async def update_app_versions(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App 版本 ID')], obj: UpdateAppVersionsParam
) -> ResponseModel:
    count = await app_versions_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App 版本',
    dependencies=[
        Depends(RequestPermission('app:versions:del')),
        DependsRBAC,
    ],
)
async def delete_app_versionss(db: CurrentSessionTransaction, obj: DeleteAppVersionsParam) -> ResponseModel:
    count = await app_versions_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
