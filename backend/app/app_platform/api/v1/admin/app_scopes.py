from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_scopes import (
    CreateAppScopesParam,
    DeleteAppScopesParam,
    GetAppScopesDetail,
    UpdateAppScopesParam,
)
from backend.app.app_platform.service.app_scopes_service import app_scopes_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取应用权限定义表（{domain}.* namespace）详情', dependencies=[DependsJwtAuth], name='admin_get_app_scopes')
async def get_app_scopes(
    db: CurrentSession, pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')]
) -> ResponseSchemaModel[GetAppScopesDetail]:
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    return response_base.success(data=app_scopes)


@router.get(
    '',
    summary='分页获取所有应用权限定义表（{domain}.* namespace）',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_scopess_paginated')
async def get_app_scopess_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppScopesDetail]]:
    page_data = await app_scopes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用权限定义表（{domain}.* namespace）',
    dependencies=[
        Depends(RequestPermission('app:scopes:add')),
        DependsRBAC,
    ],
)
async def create_app_scopes(db: CurrentSessionTransaction, obj: CreateAppScopesParam) -> ResponseModel:
    await app_scopes_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新应用权限定义表（{domain}.* namespace）',
    dependencies=[
        Depends(RequestPermission('app:scopes:edit')),
        DependsRBAC,
    ],
)
async def update_app_scopes(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')], obj: UpdateAppScopesParam
) -> ResponseModel:
    count = await app_scopes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除应用权限定义表（{domain}.* namespace）',
    dependencies=[
        Depends(RequestPermission('app:scopes:del')),
        DependsRBAC,
    ],
)
async def delete_app_scopess(db: CurrentSessionTransaction, obj: DeleteAppScopesParam) -> ResponseModel:
    count = await app_scopes_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
