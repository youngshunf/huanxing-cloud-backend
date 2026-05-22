"""Skill Bundle 定义表（多个 skill 的组合） - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_skill_bundle import (
    CreateHasnSkillBundleParam,
    UpdateHasnSkillBundleParam,
)
from backend.app.hasn.service.hasn_skill_bundle_service import hasn_skill_bundle_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='Skill Bundle 定义表（多个 skill 的组合）列表',
    dependencies=[DependsAgentJwtAuth],
    name='agent_list_hasn_skill_bundle',
)
async def agent_list_hasn_skill_bundle(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await hasn_skill_bundle_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建Skill Bundle 定义表（多个 skill 的组合）',
    dependencies=[DependsAgentJwtAuth],
    name='agent_create_hasn_skill_bundle',
)
async def agent_create_hasn_skill_bundle(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnSkillBundleParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await hasn_skill_bundle_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Skill Bundle 定义表（多个 skill 的组合）详情',
    dependencies=[DependsAgentJwtAuth],
    name='agent_get_hasn_skill_bundle',
)
async def agent_get_hasn_skill_bundle(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='Skill Bundle 定义表（多个 skill 的组合） ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_skill_bundle = await hasn_skill_bundle_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_skill_bundle.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该Skill Bundle 定义表（多个 skill 的组合）')
    return response_base.success(data=hasn_skill_bundle)


@router.put(
    '/{pk}',
    summary='更新Skill Bundle 定义表（多个 skill 的组合）',
    dependencies=[DependsAgentJwtAuth],
    name='agent_update_hasn_skill_bundle',
)
async def agent_update_hasn_skill_bundle(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Skill Bundle 定义表（多个 skill 的组合） ID')],
    obj: UpdateHasnSkillBundleParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_skill_bundle = await hasn_skill_bundle_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_skill_bundle.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该Skill Bundle 定义表（多个 skill 的组合）')
    count = await hasn_skill_bundle_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Skill Bundle 定义表（多个 skill 的组合）',
    dependencies=[DependsAgentJwtAuth],
    name='agent_delete_hasn_skill_bundle',
)
async def agent_delete_hasn_skill_bundle(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Skill Bundle 定义表（多个 skill 的组合） ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    hasn_skill_bundle = await hasn_skill_bundle_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if hasn_skill_bundle.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该Skill Bundle 定义表（多个 skill 的组合）')
    from backend.app.hasn.schema.hasn_skill_bundle import DeleteHasnSkillBundleParam
    count = await hasn_skill_bundle_service.delete(db=db, obj=DeleteHasnSkillBundleParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
