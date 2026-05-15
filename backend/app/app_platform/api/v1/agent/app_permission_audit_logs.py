"""权限审计日志 - Agent API

认证方式: Agent JWT (Bearer token)
Agent 信息: 通过 request.state.agent 获取
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_permission_audit_logs import (
    CreateAppPermissionAuditLogsParam,
    UpdateAppPermissionAuditLogsParam,
)
from backend.app.app_platform.service.app_permission_audit_logs_service import app_permission_audit_logs_service
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='权限审计日志列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_permission_audit_logss(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    # 可以使用 agent.agent_hasn_id, agent.owner_hasn_id, agent.scopes
    data = await app_permission_audit_logs_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建权限审计日志',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_permission_audit_logs(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppPermissionAuditLogsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    result = await app_permission_audit_logs_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取权限审计日志详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_permission_audit_logs(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='权限审计日志 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if app_permission_audit_logs.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权访问该权限审计日志')
    return response_base.success(data=app_permission_audit_logs)


@router.put(
    '/{pk}',
    summary='更新权限审计日志',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_permission_audit_logs(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='权限审计日志 ID')],
    obj: UpdateAppPermissionAuditLogsParam,
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if app_permission_audit_logs.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权修改该权限审计日志')
    count = await app_permission_audit_logs_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除权限审计日志',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_permission_audit_logs(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='权限审计日志 ID')],
) -> ResponseModel:
    agent: AgentTokenPayload = request.state.agent
    app_permission_audit_logs = await app_permission_audit_logs_service.get(db=db, pk=pk)
    # TODO: 根据实际业务需求添加权限检查
    # if app_permission_audit_logs.owner_id != agent.owner_hasn_id:
    #     raise errors.ForbiddenError(msg='无权删除该权限审计日志')
    from backend.app.app_platform.schema.app_permission_audit_logs import DeleteAppPermissionAuditLogsParam
    count = await app_permission_audit_logs_service.delete(db=db, obj=DeleteAppPermissionAuditLogsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
