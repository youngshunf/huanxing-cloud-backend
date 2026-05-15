from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_manifests import (
    CreateAppManifestsParam,
    DeleteAppManifestsParam,
    GetAppManifestsDetail,
    UpdateAppManifestsParam,
)
from backend.app.app_platform.service.app_manifests_service import app_manifests_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App 清单详情', dependencies=[DependsJwtAuth], name='admin_get_app_manifests')
async def get_app_manifests(
    db: CurrentSession, pk: Annotated[int, Path(description='App 清单 ID')]
) -> ResponseSchemaModel[GetAppManifestsDetail]:
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    return response_base.success(data=app_manifests)


@router.get(
    '',
    summary='分页获取所有App 清单',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_manifestss_paginated')
async def get_app_manifestss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppManifestsDetail]]:
    page_data = await app_manifests_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 清单',
    dependencies=[
        Depends(RequestPermission('app:manifests:add')),
        DependsRBAC,
    ],
)
async def create_app_manifests(db: CurrentSessionTransaction, obj: CreateAppManifestsParam) -> ResponseModel:
    await app_manifests_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App 清单',
    dependencies=[
        Depends(RequestPermission('app:manifests:edit')),
        DependsRBAC,
    ],
)
async def update_app_manifests(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App 清单 ID')], obj: UpdateAppManifestsParam
) -> ResponseModel:
    count = await app_manifests_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App 清单',
    dependencies=[
        Depends(RequestPermission('app:manifests:del')),
        DependsRBAC,
    ],
)
async def delete_app_manifestss(db: CurrentSessionTransaction, obj: DeleteAppManifestsParam) -> ResponseModel:
    count = await app_manifests_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
