"""HASN 审计日志管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_core.schema.admin.hasn_audit_log import (
    CreateHasnAuditLogParam,
    DeleteHasnAuditLogParam,
    GetHasnAuditLogDetail,
    UpdateHasnAuditLogParam,
)
from backend.app.hasn_core.service.admin.hasn_audit_log import hasn_audit_log_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取审计日志详情', dependencies=[DependsJwtAuth])
async def get_hasn_audit_log(
    db: CurrentSession, pk: Annotated[int, Path(description='审计日志 ID')]
) -> ResponseSchemaModel[GetHasnAuditLogDetail]:
    obj = await hasn_audit_log_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取审计日志列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_audit_log_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnAuditLogDetail]]:
    page_data = await hasn_audit_log_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建审计日志',
    dependencies=[Depends(RequestPermission('hasn:audit:log:add')), DependsRBAC],
)
async def create_hasn_audit_log(db: CurrentSessionTransaction, obj: CreateHasnAuditLogParam) -> ResponseModel:
    await hasn_audit_log_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新审计日志',
    dependencies=[Depends(RequestPermission('hasn:audit:log:edit')), DependsRBAC],
)
async def update_hasn_audit_log(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='审计日志 ID')],
    obj: UpdateHasnAuditLogParam,
) -> ResponseModel:
    count = await hasn_audit_log_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除审计日志',
    dependencies=[Depends(RequestPermission('hasn:audit:log:del')), DependsRBAC],
)
async def delete_hasn_audit_log(db: CurrentSessionTransaction, obj: DeleteHasnAuditLogParam) -> ResponseModel:
    count = await hasn_audit_log_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
