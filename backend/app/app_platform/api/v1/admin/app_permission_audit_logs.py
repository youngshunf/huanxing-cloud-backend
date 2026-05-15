from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_permission_audit_logs import (
    CreateAppPermissionAuditLogsParam,
    DeleteAppPermissionAuditLogsParam,
    GetAppPermissionAuditLogsDetail,
    UpdateAppPermissionAuditLogsParam,
)
from backend.app.app_platform.service.app_permission_audit_logs_service import app_permission_audit_logs_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取权限审计日志详情', dependencies=[DependsJwtAuth], name='admin_get_app_permission_audit_logs')
async def get_app_permission_audit_logs(
    db: CurrentSession, pk: Annotated[int, Path(description='权限审计日志 ID')]
) -> ResponseSchemaModel[GetAppPermissionAuditLogsDetail]:
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    return response_base.success(data=app_permission_audit_logs)


@router.get(
    '',
    summary='分页获取所有权限审计日志',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_permission_audit_logss_paginated')
async def get_app_permission_audit_logss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppPermissionAuditLogsDetail]]:
    page_data = await app_permission_audit_logs_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建权限审计日志',
    dependencies=[
        Depends(RequestPermission('app:permission:audit:logs:add')),
        DependsRBAC,
    ],
)
async def create_app_permission_audit_logs(db: CurrentSessionTransaction, obj: CreateAppPermissionAuditLogsParam) -> ResponseModel:
    await app_permission_audit_logs_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新权限审计日志',
    dependencies=[
        Depends(RequestPermission('app:permission:audit:logs:edit')),
        DependsRBAC,
    ],
)
async def update_app_permission_audit_logs(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='权限审计日志 ID')], obj: UpdateAppPermissionAuditLogsParam
) -> ResponseModel:
    count = await app_permission_audit_logs_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除权限审计日志',
    dependencies=[
        Depends(RequestPermission('app:permission:audit:logs:del')),
        DependsRBAC,
    ],
)
async def delete_app_permission_audit_logss(db: CurrentSessionTransaction, obj: DeleteAppPermissionAuditLogsParam) -> ResponseModel:
    count = await app_permission_audit_logs_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
