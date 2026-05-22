"""HASN Agent  - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""

from typing import Annotated

import sqlalchemy as sa

from fastapi import APIRouter, Path, Request
from pydantic import BaseModel, Field

from backend.app.hasn.model import HasnAgents, HasnHumans
from backend.app.hasn.schema.hasn_agents import (
    AgentSnapshot,
    AgentSyncRequest,
    AgentSyncResponse,
    CloudCreateAgentRequest,
    CloudCreateAgentResponse,
    CreateHasnAgentsParam,
    GetHasnAgentsDetail,
    UpdateAgentBindingRequest,
    UpdateAgentProfileRequest,
    UpdateAgentProfileResponse,
    UpdateHasnAgentsParam,
)
from backend.app.hasn.service.hasn_agents_service import agent_profile_service, hasn_agents_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '/sync',
    summary='同步云端 HASN Agent Profile 快照',
    dependencies=[DependsJwtAuth],
)
async def sync_my_hasn_agents(
    request: Request,
    db: CurrentSession,
    owner_id: str,
    after_revision: int | None = None,
) -> ResponseSchemaModel[AgentSyncResponse]:
    result = await agent_profile_service.sync_agents(
        db=db,
        request=AgentSyncRequest(owner_id=owner_id, after_revision=after_revision),
        user_id=request.user.id,
    )
    return response_base.success(data=result)


@router.post(
    '/cloud-create',
    summary='云端优先创建 HASN Agent Profile',
    dependencies=[DependsJwtAuth],
)
async def cloud_create_my_hasn_agent(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CloudCreateAgentRequest,
) -> ResponseSchemaModel[CloudCreateAgentResponse]:
    result = await agent_profile_service.create_cloud_first(db=db, request=obj, user_id=request.user.id)
    return response_base.success(data=result)


@router.get(
    '',
    summary='获取我的HASN Agent 列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_hasn_agentss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnAgentsDetail]]:
    page_data = await hasn_agents_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN Agent ',
    dependencies=[DependsJwtAuth],
)
async def create_my_hasn_agents(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnAgentsParam,
) -> ResponseModel:
    result = await hasn_agents_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN Agent 详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_hasn_agents(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
) -> ResponseSchemaModel[GetHasnAgentsDetail]:
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该HASN Agent ')
    return response_base.success(data=hasn_agents)


@router.put(
    '/{pk}',
    summary='更新HASN Agent ',
    dependencies=[DependsJwtAuth],
)
async def update_my_hasn_agents(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
    obj: UpdateHasnAgentsParam,
) -> ResponseModel:
    user_id = request.user.id
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Agent ')
    count = await hasn_agents_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


class ToggleSocialBody(BaseModel):
    enabled: bool = Field(description='目标 social_enabled 值')


@router.patch(
    '/by-hasn-id/{hasn_id}',
    summary='daemon 端 Agent Profile 部分更新（云端权威）',
    dependencies=[DependsJwtAuth],
)
async def update_my_hasn_agent_profile(
    request: Request,
    db: CurrentSessionTransaction,
    hasn_id: Annotated[str, Path(description='Agent HASN ID, 如 a_xxx')],
    body: UpdateAgentProfileRequest,
) -> ResponseSchemaModel[UpdateAgentProfileResponse]:
    """daemon 用 hasn_id 更新 Agent profile：display_name/description/avatar 部分字段。

    云端先落库后返回最新 AgentSnapshot；daemon 据此回写本地镜像，保证 daemon 与云端一致。
    """
    user_id = request.user.id
    owner = (await db.execute(sa.select(HasnHumans.hasn_id).where(HasnHumans.user_id == user_id))).scalar_one_or_none()
    if not owner:
        raise errors.ForbiddenError(msg='当前用户未注册 HASN 身份')
    result = await agent_profile_service.update_profile_cloud_first(
        db,
        owner_id=owner,
        hasn_id=hasn_id,
        request=body,
        user_id=user_id,
    )
    return response_base.success(data=result)


@router.patch(
    '/by-hasn-id/{hasn_id}/binding',
    summary='daemon 端更新 Agent binding 状态',
    dependencies=[DependsJwtAuth],
)
async def update_my_hasn_agent_binding(
    request: Request,
    db: CurrentSessionTransaction,
    hasn_id: Annotated[str, Path(description='Agent HASN ID, 如 a_xxx')],
    body: UpdateAgentBindingRequest,
) -> ResponseSchemaModel[AgentSnapshot]:
    """daemon 在 activate binding 后调用，同步 binding_node_id 和 binding_status 到云端。"""
    result = await agent_profile_service.update_binding(
        db,
        hasn_id=hasn_id,
        request=body,
        user_id=request.user.id,
    )
    return response_base.success(data=result)


@router.post(
    '/{hasn_id}/social/toggle',
    summary='切换 Agent social_enabled (按 hasn_id, daemon 同步用)',
    dependencies=[DependsJwtAuth],
)
async def toggle_my_hasn_agent_social(
    request: Request,
    db: CurrentSessionTransaction,
    hasn_id: Annotated[str, Path(description='Agent HASN ID, 如 a_xxx')],
    body: ToggleSocialBody,
) -> ResponseModel:
    user_id = request.user.id
    owner = (await db.execute(sa.select(HasnHumans.hasn_id).where(HasnHumans.user_id == user_id))).scalar_one_or_none()
    if not owner:
        raise errors.ForbiddenError(msg='当前用户未注册 HASN 身份')
    agent = (
        await db.execute(
            sa.select(HasnAgents).where(
                HasnAgents.hasn_id == hasn_id,
                HasnAgents.owner_id == owner,
            )
        )
    ).scalar_one_or_none()
    if not agent:
        raise errors.NotFoundError(msg='Agent 不存在或不属于当前用户')
    agent.social_enabled = body.enabled
    if hasattr(agent, 'profile_revision'):
        agent.profile_revision = (agent.profile_revision or 1) + 1
    await db.flush()
    return response_base.success(
        data={
            'hasn_id': agent.hasn_id,
            'social_enabled': agent.social_enabled,
        }
    )


@router.delete(
    '/{pk}',
    summary='删除HASN Agent ',
    dependencies=[DependsJwtAuth],
)
async def delete_my_hasn_agents(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Agent  ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_agents = await hasn_agents_service.get(db=db, pk=pk)
    if hasn_agents.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Agent ')
    from backend.app.hasn.schema.hasn_agents import DeleteHasnAgentsParam

    count = await hasn_agents_service.delete(db=db, obj=DeleteHasnAgentsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
