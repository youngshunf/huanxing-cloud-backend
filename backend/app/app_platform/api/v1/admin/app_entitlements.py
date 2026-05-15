from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_entitlements import (
    CreateAppEntitlementsParam,
    DeleteAppEntitlementsParam,
    GetAppEntitlementsDetail,
    UpdateAppEntitlementsParam,
)
from backend.app.app_platform.service.app_entitlements_service import app_entitlements_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App 购买凭证详情', dependencies=[DependsJwtAuth], name='admin_get_app_entitlements')
async def get_app_entitlements(
    db: CurrentSession, pk: Annotated[int, Path(description='App 购买凭证 ID')]
) -> ResponseSchemaModel[GetAppEntitlementsDetail]:
    app_entitlements = await app_entitlements_service.get(db=db, pk=pk)
    return response_base.success(data=app_entitlements)


@router.get(
    '',
    summary='分页获取所有App 购买凭证',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_entitlementss_paginated')
async def get_app_entitlementss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppEntitlementsDetail]]:
    page_data = await app_entitlements_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 购买凭证',
    dependencies=[
        Depends(RequestPermission('app:entitlements:add')),
        DependsRBAC,
    ],
)
async def create_app_entitlements(db: CurrentSessionTransaction, obj: CreateAppEntitlementsParam) -> ResponseModel:
    await app_entitlements_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App 购买凭证',
    dependencies=[
        Depends(RequestPermission('app:entitlements:edit')),
        DependsRBAC,
    ],
)
async def update_app_entitlements(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App 购买凭证 ID')], obj: UpdateAppEntitlementsParam
) -> ResponseModel:
    count = await app_entitlements_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App 购买凭证',
    dependencies=[
        Depends(RequestPermission('app:entitlements:del')),
        DependsRBAC,
    ],
)
async def delete_app_entitlementss(db: CurrentSessionTransaction, obj: DeleteAppEntitlementsParam) -> ResponseModel:
    count = await app_entitlements_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
