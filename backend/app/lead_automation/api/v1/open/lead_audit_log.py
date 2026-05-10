"""Lead automation PII and compliance audit log - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.lead_automation.schema.lead_audit_log import GetLeadAuditLogDetail
from backend.app.lead_automation.service.lead_audit_log_service import lead_audit_log_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取Lead automation PII and compliance audit log列表',
    dependencies=[DependsPagination],
)
async def get_lead_audit_logs(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetLeadAuditLogDetail]]:
    page_data = await lead_audit_log_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取Lead automation PII and compliance audit log详情',
)
async def get_lead_audit_log(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Lead automation PII and compliance audit log ID')],
) -> ResponseSchemaModel[GetLeadAuditLogDetail]:
    lead_audit_log = await lead_audit_log_service.get(db=db, pk=pk)
    return response_base.success(data=lead_audit_log)
