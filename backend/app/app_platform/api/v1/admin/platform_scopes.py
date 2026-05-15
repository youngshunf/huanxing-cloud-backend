from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.platform_scopes import (
    CreatePlatformScopesParam,
    DeletePlatformScopesParam,
    GetPlatformScopesDetail,
    UpdatePlatformScopesParam,
)
from backend.app.app_platform.service.platform_scopes_service import platform_scopes_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取平台权限定义表（hasn.* namespace）详情', dependencies=[DependsJwtAuth], name='admin_get_platform_scopes')
async def get_platform_scopes(
    db: CurrentSession, pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')]
) -> ResponseSchemaModel[GetPlatformScopesDetail]:
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    return response_base.success(data=platform_scopes)


@router.get(
    '',
    summary='分页获取所有平台权限定义表（hasn.* namespace）',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_platform_scopess_paginated')
async def get_platform_scopess_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetPlatformScopesDetail]]:
    page_data = await platform_scopes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建平台权限定义表（hasn.* namespace）',
    dependencies=[
        Depends(RequestPermission('platform:scopes:add')),
        DependsRBAC,
    ],
)
async def create_platform_scopes(db: CurrentSessionTransaction, obj: CreatePlatformScopesParam) -> ResponseModel:
    await platform_scopes_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新平台权限定义表（hasn.* namespace）',
    dependencies=[
        Depends(RequestPermission('platform:scopes:edit')),
        DependsRBAC,
    ],
)
async def update_platform_scopes(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')], obj: UpdatePlatformScopesParam
) -> ResponseModel:
    count = await platform_scopes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除平台权限定义表（hasn.* namespace）',
    dependencies=[
        Depends(RequestPermission('platform:scopes:del')),
        DependsRBAC,
    ],
)
async def delete_platform_scopess(db: CurrentSessionTransaction, obj: DeletePlatformScopesParam) -> ResponseModel:
    count = await platform_scopes_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
