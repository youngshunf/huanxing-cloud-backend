"""权限审计日志 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_permission_audit_logs import (
    CreateAppPermissionAuditLogsParam,
    GetAppPermissionAuditLogsDetail,
    UpdateAppPermissionAuditLogsParam,
)
from backend.app.app_platform.service.app_permission_audit_logs_service import app_permission_audit_logs_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的权限审计日志列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_permission_audit_logss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppPermissionAuditLogsDetail]]:
    page_data = await app_permission_audit_logs_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建权限审计日志',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_permission_audit_logs(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppPermissionAuditLogsParam,
) -> ResponseModel:
    result = await app_permission_audit_logs_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取权限审计日志详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_permission_audit_logs(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='权限审计日志 ID')],
) -> ResponseSchemaModel[GetAppPermissionAuditLogsDetail]:
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    if app_permission_audit_logs.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该权限审计日志')
    return response_base.success(data=app_permission_audit_logs)


@router.put(
    '/{pk}',
    summary='更新权限审计日志',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_permission_audit_logs(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='权限审计日志 ID')],
    obj: UpdateAppPermissionAuditLogsParam,
) -> ResponseModel:
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    if getattr(app_permission_audit_logs, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该权限审计日志')
    count = await app_permission_audit_logs_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除权限审计日志',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_permission_audit_logs(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='权限审计日志 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    if app_permission_audit_logs.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该权限审计日志')
    from backend.app.app_platform.schema.app_permission_audit_logs import DeleteAppPermissionAuditLogsParam
    count = await app_permission_audit_logs_service.delete(db=db, obj=DeleteAppPermissionAuditLogsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
