"""Firecrawl request audit for AI lead automation - Agent API

认证方式: DependsAgentAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.lead_automation.schema.lead_firecrawl_request import (
    CreateLeadFirecrawlRequestParam,
    UpdateLeadFirecrawlRequestParam,
)
from backend.app.lead_automation.service.lead_firecrawl_request_service import lead_firecrawl_request_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_auth import DependsAgentAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='Firecrawl request audit for AI lead automation列表',
    dependencies=[DependsAgentAuth],
)
async def agent_list_lead_firecrawl_requests(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await lead_firecrawl_request_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建Firecrawl request audit for AI lead automation',
    dependencies=[DependsAgentAuth],
)
async def agent_create_lead_firecrawl_request(
    db: CurrentSessionTransaction,
    obj: CreateLeadFirecrawlRequestParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await lead_firecrawl_request_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Firecrawl request audit for AI lead automation详情',
    dependencies=[DependsAgentAuth],
)
async def agent_get_lead_firecrawl_request(
    db: CurrentSession,
    pk: Annotated[int, Path(description='Firecrawl request audit for AI lead automation ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_firecrawl_request = await lead_firecrawl_request_service.get(db=db, pk=pk)
    if lead_firecrawl_request.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该Firecrawl request audit for AI lead automation')
    return response_base.success(data=lead_firecrawl_request)


@router.put(
    '/{pk}',
    summary='更新Firecrawl request audit for AI lead automation',
    dependencies=[DependsAgentAuth],
)
async def agent_update_lead_firecrawl_request(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Firecrawl request audit for AI lead automation ID')],
    obj: UpdateLeadFirecrawlRequestParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_firecrawl_request = await lead_firecrawl_request_service.get(db=db, pk=pk)
    if lead_firecrawl_request.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该Firecrawl request audit for AI lead automation')
    count = await lead_firecrawl_request_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Firecrawl request audit for AI lead automation',
    dependencies=[DependsAgentAuth],
)
async def agent_delete_lead_firecrawl_request(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Firecrawl request audit for AI lead automation ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    lead_firecrawl_request = await lead_firecrawl_request_service.get(db=db, pk=pk)
    if lead_firecrawl_request.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Firecrawl request audit for AI lead automation')
    from backend.app.lead_automation.schema.lead_firecrawl_request import DeleteLeadFirecrawlRequestParam
    count = await lead_firecrawl_request_service.delete(db=db, obj=DeleteLeadFirecrawlRequestParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
