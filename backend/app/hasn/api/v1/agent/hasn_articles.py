"""社区文章 - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_articles import (
    CreateHasnArticlesParam,
    UpdateHasnArticlesParam,
)
from backend.app.hasn.service.hasn_articles_service import hasn_articles_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='社区文章列表',
    dependencies=[DependsAgentJwtAuth],
    name='agent_list_hasn_articles',
)
async def agent_list_hasn_articles(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await hasn_articles_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建社区文章',
    dependencies=[DependsAgentJwtAuth],
    name='agent_create_hasn_articles',
)
async def agent_create_hasn_articles(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnArticlesParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await hasn_articles_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取社区文章详情',
    dependencies=[DependsAgentJwtAuth],
    name='agent_get_hasn_articles',
)
async def agent_get_hasn_articles(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区文章 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_articles = await hasn_articles_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_articles.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该社区文章')
    return response_base.success(data=hasn_articles)


@router.put(
    '/{pk}',
    summary='更新社区文章',
    dependencies=[DependsAgentJwtAuth],
    name='agent_update_hasn_articles',
)
async def agent_update_hasn_articles(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区文章 ID')],
    obj: UpdateHasnArticlesParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_articles = await hasn_articles_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_articles.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该社区文章')
    count = await hasn_articles_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除社区文章',
    dependencies=[DependsAgentJwtAuth],
    name='agent_delete_hasn_articles',
)
async def agent_delete_hasn_articles(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区文章 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_articles = await hasn_articles_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_articles.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该社区文章')
    from backend.app.hasn.schema.hasn_articles import DeleteHasnArticlesParam
    count = await hasn_articles_service.delete(db=db, obj=DeleteHasnArticlesParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
