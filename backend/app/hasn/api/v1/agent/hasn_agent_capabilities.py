"""HASN Agent 能力声明 - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.hasn.schema.hasn_agent_capabilities import (
    CreateHasnAgentCapabilitiesParam,
    UpdateHasnAgentCapabilitiesParam,
)
from backend.app.hasn.service.hasn_agent_capabilities_service import hasn_agent_capabilities_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='HASN Agent 能力声明列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_hasn_agent_capabilitiess(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await hasn_agent_capabilities_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建HASN Agent 能力声明',
    dependencies=[DependsAgentAuth],
)
async def agent_create_hasn_agent_capabilities(
    db: CurrentSessionTransaction,
    obj: CreateHasnAgentCapabilitiesParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await hasn_agent_capabilities_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN Agent 能力声明详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_hasn_agent_capabilities(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Agent 能力声明 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_agent_capabilities = await hasn_agent_capabilities_service.get(db=db, pk=pk)
    if hasn_agent_capabilities.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该HASN Agent 能力声明')
    return response_base.success(data=hasn_agent_capabilities)


@router.put(
    '/{pk}',
    summary='更新HASN Agent 能力声明',
    dependencies=[DependsAgentAuth],
)
async def agent_update_hasn_agent_capabilities(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Agent 能力声明 ID')],
    obj: UpdateHasnAgentCapabilitiesParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_agent_capabilities = await hasn_agent_capabilities_service.get(db=db, pk=pk)
    if hasn_agent_capabilities.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Agent 能力声明')
    count = await hasn_agent_capabilities_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN Agent 能力声明',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_hasn_agent_capabilities(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Agent 能力声明 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    hasn_agent_capabilities = await hasn_agent_capabilities_service.get(db=db, pk=pk)
    if hasn_agent_capabilities.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Agent 能力声明')
    from backend.app.hasn.schema.hasn_agent_capabilities import DeleteHasnAgentCapabilitiesParam
    count = await hasn_agent_capabilities_service.delete(db=db, obj=DeleteHasnAgentCapabilitiesParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
