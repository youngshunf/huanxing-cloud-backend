"""Lead automation PII and compliance audit log - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.lead_automation.schema.lead_audit_log import (
    CreateLeadAuditLogParam,
    UpdateLeadAuditLogParam,
)
from backend.app.lead_automation.service.lead_audit_log_service import lead_audit_log_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='Lead automation PII and compliance audit log列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_lead_audit_logs(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await lead_audit_log_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建Lead automation PII and compliance audit log',
    dependencies=[DependsAgentAuth],
)
async def agent_create_lead_audit_log(
    db: CurrentSessionTransaction,
    obj: CreateLeadAuditLogParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await lead_audit_log_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Lead automation PII and compliance audit log详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_lead_audit_log(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Lead automation PII and compliance audit log ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_audit_log = await lead_audit_log_service.get(db=db, pk=pk)
    if lead_audit_log.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该Lead automation PII and compliance audit log')
    return response_base.success(data=lead_audit_log)


@router.put(
    '/{pk}',
    summary='更新Lead automation PII and compliance audit log',
    dependencies=[DependsAgentAuth],
)
async def agent_update_lead_audit_log(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Lead automation PII and compliance audit log ID')],
    obj: UpdateLeadAuditLogParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_audit_log = await lead_audit_log_service.get(db=db, pk=pk)
    if lead_audit_log.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该Lead automation PII and compliance audit log')
    count = await lead_audit_log_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Lead automation PII and compliance audit log',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_lead_audit_log(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Lead automation PII and compliance audit log ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_audit_log = await lead_audit_log_service.get(db=db, pk=pk)
    if lead_audit_log.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Lead automation PII and compliance audit log')
    from backend.app.lead_automation.schema.lead_audit_log import DeleteLeadAuditLogParam
    count = await lead_audit_log_service.delete(db=db, obj=DeleteLeadAuditLogParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
