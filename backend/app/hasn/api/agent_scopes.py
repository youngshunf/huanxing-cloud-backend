"""Agent 权限管理路由"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao
from backend.app.hasn.schema.agent_scopes import (
    AgentScopesConfig,
    UpdateAgentScopesRequest,
    UpdateAgentScopesResponse,
)
from backend.app.hasn.service.agent_scopes_service import agent_scopes_service
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import get_db

router = APIRouter()


@router.get(
    '/community/settings/agents/{agent_hasn_id}',
    summary='查询 Agent 权限配置',
    description='查询指定 Agent 的权限配置（需要 Owner JWT）',
    dependencies=[DependsJwtAuth],
)
async def get_agent_scopes(
    request: Request,
    agent_hasn_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AgentScopesConfig:
    """查询 Agent 权限配置"""
    # 获取 Owner HASN ID
    human = await hasn_humans_dao.get_by_user_id(db, user_id=request.user.id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='未找到对应的 HASN Human 记录')

    return await agent_scopes_service.get_agent_scopes(
        db=db,
        agent_hasn_id=agent_hasn_id,
        owner_hasn_id=human.hasn_id,
    )


@router.put(
    '/community/settings/agents/{agent_hasn_id}',
    summary='更新 Agent 权限配置',
    description='更新指定 Agent 的权限配置，并重新签发 Agent JWT（需要 Owner JWT）',
    dependencies=[DependsJwtAuth],
)
async def update_agent_scopes(
    request: Request,
    agent_hasn_id: str,
    request_body: UpdateAgentScopesRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UpdateAgentScopesResponse:
    """更新 Agent 权限配置"""
    # 获取 Owner HASN ID
    human = await hasn_humans_dao.get_by_user_id(db, user_id=request.user.id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='未找到对应的 HASN Human 记录')

    return await agent_scopes_service.update_agent_scopes(
        db=db,
        agent_hasn_id=agent_hasn_id,
        owner_hasn_id=human.hasn_id,
        owner_user_id=request.user.id,
        request=request_body,
    )
