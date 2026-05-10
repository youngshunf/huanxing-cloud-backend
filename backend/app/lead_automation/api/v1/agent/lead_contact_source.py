"""Lead multi-source evidence - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.lead_automation.schema.lead_contact_source import (
    CreateLeadContactSourceParam,
    UpdateLeadContactSourceParam,
)
from backend.app.lead_automation.service.lead_contact_source_service import lead_contact_source_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='Lead multi-source evidence列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_lead_contact_sources(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await lead_contact_source_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建Lead multi-source evidence',
    dependencies=[DependsAgentAuth],
)
async def agent_create_lead_contact_source(
    db: CurrentSessionTransaction,
    obj: CreateLeadContactSourceParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await lead_contact_source_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Lead multi-source evidence详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_lead_contact_source(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Lead multi-source evidence ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_contact_source = await lead_contact_source_service.get(db=db, pk=pk)
    if lead_contact_source.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该Lead multi-source evidence')
    return response_base.success(data=lead_contact_source)


@router.put(
    '/{pk}',
    summary='更新Lead multi-source evidence',
    dependencies=[DependsAgentAuth],
)
async def agent_update_lead_contact_source(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Lead multi-source evidence ID')],
    obj: UpdateLeadContactSourceParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_contact_source = await lead_contact_source_service.get(db=db, pk=pk)
    if lead_contact_source.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该Lead multi-source evidence')
    count = await lead_contact_source_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Lead multi-source evidence',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_lead_contact_source(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Lead multi-source evidence ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_contact_source = await lead_contact_source_service.get(db=db, pk=pk)
    if lead_contact_source.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Lead multi-source evidence')
    from backend.app.lead_automation.schema.lead_contact_source import DeleteLeadContactSourceParam
    count = await lead_contact_source_service.delete(db=db, obj=DeleteLeadContactSourceParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
