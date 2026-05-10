"""Raw crawled lead page record - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.lead_automation.schema.lead_raw_record import (
    CreateLeadRawRecordParam,
    UpdateLeadRawRecordParam,
)
from backend.app.lead_automation.service.lead_raw_record_service import lead_raw_record_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='Raw crawled lead page record列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_lead_raw_records(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await lead_raw_record_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建Raw crawled lead page record',
    dependencies=[DependsAgentAuth],
)
async def agent_create_lead_raw_record(
    db: CurrentSessionTransaction,
    obj: CreateLeadRawRecordParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await lead_raw_record_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Raw crawled lead page record详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_lead_raw_record(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Raw crawled lead page record ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_raw_record = await lead_raw_record_service.get(db=db, pk=pk)
    if lead_raw_record.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该Raw crawled lead page record')
    return response_base.success(data=lead_raw_record)


@router.put(
    '/{pk}',
    summary='更新Raw crawled lead page record',
    dependencies=[DependsAgentAuth],
)
async def agent_update_lead_raw_record(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Raw crawled lead page record ID')],
    obj: UpdateLeadRawRecordParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_raw_record = await lead_raw_record_service.get(db=db, pk=pk)
    if lead_raw_record.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该Raw crawled lead page record')
    count = await lead_raw_record_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Raw crawled lead page record',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_lead_raw_record(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Raw crawled lead page record ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_raw_record = await lead_raw_record_service.get(db=db, pk=pk)
    if lead_raw_record.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Raw crawled lead page record')
    from backend.app.lead_automation.schema.lead_raw_record import DeleteLeadRawRecordParam
    count = await lead_raw_record_service.delete(db=db, obj=DeleteLeadRawRecordParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
