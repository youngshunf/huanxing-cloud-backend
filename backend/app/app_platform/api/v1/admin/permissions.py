"""
权限管理 API

提供权限授予、撤销、动态请求等高级功能
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body
from pydantic import BaseModel, Field

from backend.app.app_platform.service.permission_service import permission_service
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


# ============================================================================
# Request/Response Schemas
# ============================================================================

class GrantScopesRequest(BaseModel):
    """授予权限请求"""
    installation_id: str = Field(..., description='Installation ID')
    scopes: list[str] = Field(..., description='权限列表')
    granted_by: str = Field(..., description='授予者 Owner ID')
    grant_source: str = Field(default='installation', description='授予来源')


class RevokeScopeRequest(BaseModel):
    """撤销权限请求"""
    installation_id: str = Field(..., description='Installation ID')
    scope: str = Field(..., description='权限标识')
    revoked_by: str = Field(..., description='撤销者')
    revocation_reason: str | None = Field(None, description='撤销原因')


class DynamicPermissionRequest(BaseModel):
    """动态权限请求"""
    installation_id: str = Field(..., description='Installation ID')
    scope: str = Field(..., description='权限标识')
    request_reason: str = Field(..., description='请求原因')
    request_context: dict | None = Field(None, description='请求上下文')


class ApproveDynamicPermissionRequest(BaseModel):
    """批准动态权限请求"""
    request_id: str = Field(..., description='请求 ID')
    decided_by: str = Field(..., description='决策者 Owner ID')
    decision_reason: str | None = Field(None, description='决策理由')


class DenyDynamicPermissionRequest(BaseModel):
    """拒绝动态权限请求"""
    request_id: str = Field(..., description='请求 ID')
    decided_by: str = Field(..., description='决策者 Owner ID')
    decision_reason: str | None = Field(None, description='决策理由')


# ============================================================================
# API Endpoints
# ============================================================================

@router.post(
    '/grant',
    summary='授予权限',
    description='为 Installation 授予一组权限',
    dependencies=[
        Depends(RequestPermission('app:permission:grant')),
        DependsRBAC,
    ],
)
async def grant_scopes(
    db: CurrentSessionTransaction,
    req: GrantScopesRequest,
) -> ResponseModel:
    """
    授予权限

    为指定的 Installation 授予一组权限。
    """
    await permission_service.grant_scopes(
        db=db,
        installation_id=req.installation_id,
        scopes=req.scopes,
        granted_by=req.granted_by,
        grant_source=req.grant_source,
    )
    return response_base.success(msg='权限授予成功')


@router.post(
    '/revoke',
    summary='撤销权限',
    description='撤销 Installation 的某个权限',
    dependencies=[
        Depends(RequestPermission('app:permission:revoke')),
        DependsRBAC,
    ],
)
async def revoke_scope(
    db: CurrentSessionTransaction,
    req: RevokeScopeRequest,
) -> ResponseModel:
    """
    撤销权限

    撤销指定 Installation 的某个权限。
    """
    await permission_service.revoke_scope(
        db=db,
        installation_id=req.installation_id,
        scope=req.scope,
        revoked_by=req.revoked_by,
        revocation_reason=req.revocation_reason,
    )
    return response_base.success(msg='权限撤销成功')


@router.post(
    '/request',
    summary='动态权限请求',
    description='App 运行时动态请求额外权限',
    dependencies=[DependsJwtAuth],
 name='admin_request_dynamic_permission')
async def request_dynamic_permission(
    db: CurrentSessionTransaction,
    req: DynamicPermissionRequest,
) -> ResponseSchemaModel[dict]:
    """
    动态权限请求

    App 在运行时请求额外的权限，需要 Owner 批准。
    """
    result = await permission_service.request_dynamic_permission(
        db=db,
        installation_id=req.installation_id,
        scope=req.scope,
        request_reason=req.request_reason,
        request_context=req.request_context,
    )
    return response_base.success(data=result)


@router.post(
    '/approve',
    summary='批准动态权限请求',
    description='Owner 批准 App 的动态权限请求',
    dependencies=[
        Depends(RequestPermission('app:permission:approve')),
        DependsRBAC,
    ],
)
async def approve_dynamic_permission(
    db: CurrentSessionTransaction,
    req: ApproveDynamicPermissionRequest,
) -> ResponseModel:
    """
    批准动态权限请求

    Owner 批准 App 的动态权限请求，权限将被授予。
    """
    await permission_service.approve_dynamic_permission_request(
        db=db,
        request_id=req.request_id,
        decided_by=req.decided_by,
        decision_reason=req.decision_reason,
    )
    return response_base.success(msg='权限请求已批准')


@router.post(
    '/deny',
    summary='拒绝动态权限请求',
    description='Owner 拒绝 App 的动态权限请求',
    dependencies=[
        Depends(RequestPermission('app:permission:deny')),
        DependsRBAC,
    ],
)
async def deny_dynamic_permission(
    db: CurrentSessionTransaction,
    req: DenyDynamicPermissionRequest,
) -> ResponseModel:
    """
    拒绝动态权限请求

    Owner 拒绝 App 的动态权限请求。
    """
    await permission_service.deny_dynamic_permission_request(
        db=db,
        request_id=req.request_id,
        decided_by=req.decided_by,
        decision_reason=req.decision_reason,
    )
    return response_base.success(msg='权限请求已拒绝')


@router.get(
    '/audit',
    summary='获取权限审计日志',
    description='查询权限使用和授权的审计日志',
    dependencies=[DependsJwtAuth],
 name='admin_get_permission_audit_logs')
async def get_permission_audit_logs(
    db: CurrentSession,
    installation_id: Annotated[str | None, Path(description='Installation ID')] = None,
    scope: Annotated[str | None, Path(description='权限标识')] = None,
) -> ResponseSchemaModel[list]:
    """
    获取权限审计日志

    查询指定 Installation 或权限的审计日志。
    """
    # TODO: 实现审计日志查询
    # 需要先创建 app_permission_audit_logs 表
    return response_base.success(data=[])
