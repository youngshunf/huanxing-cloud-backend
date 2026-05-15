"""权限审计日志 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_permission_audit_logs import GetAppPermissionAuditLogsDetail
from backend.app.app_platform.service.app_permission_audit_logs_service import app_permission_audit_logs_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取权限审计日志列表',
    dependencies=[DependsPagination],
 name='open_get_app_permission_audit_logss')
async def get_app_permission_audit_logss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppPermissionAuditLogsDetail]]:
    page_data = await app_permission_audit_logs_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取权限审计日志详情',
 name='open_get_app_permission_audit_logs')
async def get_app_permission_audit_logs(
    db: CurrentSession,
    pk: Annotated[int, Path(description='权限审计日志 ID')],
) -> ResponseSchemaModel[GetAppPermissionAuditLogsDetail]:
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    return response_base.success(data=app_permission_audit_logs)
