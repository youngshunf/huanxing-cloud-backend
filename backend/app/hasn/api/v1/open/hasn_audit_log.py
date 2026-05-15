"""HASN 审计日志 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_audit_log import GetHasnAuditLogDetail
from backend.app.hasn.service.hasn_audit_log_service import hasn_audit_log_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取HASN 审计日志列表',
    dependencies=[DependsPagination],
 name='open_open_get_hasn_audit_logs')
async def open_get_hasn_audit_logs(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnAuditLogDetail]]:
    page_data = await hasn_audit_log_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取HASN 审计日志详情',
 name='open_open_get_hasn_audit_log')
async def open_get_hasn_audit_log(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 审计日志 ID')],
) -> ResponseSchemaModel[GetHasnAuditLogDetail]:
    hasn_audit_log = await hasn_audit_log_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_audit_log)
