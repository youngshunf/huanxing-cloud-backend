"""应用数据记录表（JSONB 存储） - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_data_records import (
    CreateAppDataRecordsParam,
    UpdateAppDataRecordsParam,
)
from backend.app.app_platform.service.app_data_records_service import app_data_records_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='应用数据记录表（JSONB 存储）列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_data_recordss(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await app_data_records_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建应用数据记录表（JSONB 存储）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_data_records(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppDataRecordsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await app_data_records_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取应用数据记录表（JSONB 存储）详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_data_records(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if app_data_records.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该应用数据记录表（JSONB 存储）')
    return response_base.success(data=app_data_records)


@router.put(
    '/{pk}',
    summary='更新应用数据记录表（JSONB 存储）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_data_records(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')],
    obj: UpdateAppDataRecordsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if app_data_records.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该应用数据记录表（JSONB 存储）')
    count = await app_data_records_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除应用数据记录表（JSONB 存储）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_data_records(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if app_data_records.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该应用数据记录表（JSONB 存储）')
    from backend.app.app_platform.schema.app_data_records import DeleteAppDataRecordsParam
    count = await app_data_records_service.delete(db=db, obj=DeleteAppDataRecordsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
