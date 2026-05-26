"""技能市场下载历史 - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.marketplace.schema.marketplace_download_history import (
    CreateMarketplaceDownloadHistoryParam,
    UpdateMarketplaceDownloadHistoryParam,
)
from backend.app.marketplace.service.marketplace_download_history_service import marketplace_download_history_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='技能市场下载历史列表',
    dependencies=[DependsAgentJwtAuth],
    name='agent_list_marketplace_download_history',
)
async def agent_list_marketplace_download_history(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await marketplace_download_history_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建技能市场下载历史',
    dependencies=[DependsAgentJwtAuth],
    name='agent_create_marketplace_download_history',
)
async def agent_create_marketplace_download_history(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateMarketplaceDownloadHistoryParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await marketplace_download_history_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取技能市场下载历史详情',
    dependencies=[DependsAgentJwtAuth],
    name='agent_get_marketplace_download_history',
)
async def agent_get_marketplace_download_history(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='技能市场下载历史 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    marketplace_download_history = await marketplace_download_history_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if marketplace_download_history.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该技能市场下载历史')
    return response_base.success(data=marketplace_download_history)


@router.put(
    '/{pk}',
    summary='更新技能市场下载历史',
    dependencies=[DependsAgentJwtAuth],
    name='agent_update_marketplace_download_history',
)
async def agent_update_marketplace_download_history(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='技能市场下载历史 ID')],
    obj: UpdateMarketplaceDownloadHistoryParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    marketplace_download_history = await marketplace_download_history_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if marketplace_download_history.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该技能市场下载历史')
    count = await marketplace_download_history_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除技能市场下载历史',
    dependencies=[DependsAgentJwtAuth],
    name='agent_delete_marketplace_download_history',
)
async def agent_delete_marketplace_download_history(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='技能市场下载历史 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    marketplace_download_history = await marketplace_download_history_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if marketplace_download_history.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该技能市场下载历史')
    from backend.app.marketplace.schema.marketplace_download_history import DeleteMarketplaceDownloadHistoryParam
    count = await marketplace_download_history_service.delete(db=db, obj=DeleteMarketplaceDownloadHistoryParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
