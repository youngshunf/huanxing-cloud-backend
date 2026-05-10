"""Valid deduplicated lead contact - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.lead_automation.schema.lead_contact import (
    CreateLeadContactParam,
    UpdateLeadContactParam,
)
from backend.app.lead_automation.service.lead_contact_service import lead_contact_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='Valid deduplicated lead contact列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_lead_contacts(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await lead_contact_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建Valid deduplicated lead contact',
    dependencies=[DependsAgentAuth],
)
async def agent_create_lead_contact(
    db: CurrentSessionTransaction,
    obj: CreateLeadContactParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await lead_contact_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Valid deduplicated lead contact详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_lead_contact(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Valid deduplicated lead contact ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_contact = await lead_contact_service.get(db=db, pk=pk)
    if lead_contact.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该Valid deduplicated lead contact')
    return response_base.success(data=lead_contact)


@router.put(
    '/{pk}',
    summary='更新Valid deduplicated lead contact',
    dependencies=[DependsAgentAuth],
)
async def agent_update_lead_contact(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Valid deduplicated lead contact ID')],
    obj: UpdateLeadContactParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_contact = await lead_contact_service.get(db=db, pk=pk)
    if lead_contact.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该Valid deduplicated lead contact')
    count = await lead_contact_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Valid deduplicated lead contact',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_lead_contact(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Valid deduplicated lead contact ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_contact = await lead_contact_service.get(db=db, pk=pk)
    if lead_contact.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Valid deduplicated lead contact')
    from backend.app.lead_automation.schema.lead_contact import DeleteLeadContactParam
    count = await lead_contact_service.delete(db=db, obj=DeleteLeadContactParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
