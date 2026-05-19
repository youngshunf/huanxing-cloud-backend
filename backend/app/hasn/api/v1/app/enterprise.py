from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.app.hasn.service.workbench_domain_service import workbench_domain_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction  # noqa: TC001

router = APIRouter()


class CreateEnterpriseRequest(BaseModel):
    name: str = Field(description='企业名称')
    slug: str = Field(description='企业唯一标识')
    description: str | None = None
    join_policy: str = 'invite_only'


class ApplyEnterpriseRequest(BaseModel):
    apply_message: str | None = None
    invite_code: str | None = None


class RejectApplicationRequest(BaseModel):
    note: str | None = None


class CreateInviteCodeRequest(BaseModel):
    max_uses: int | None = None
    expires_at: datetime | None = None
    auto_approve: bool = False


@router.post('/enterprises', dependencies=[DependsJwtAuth], summary='创建企业')
async def create_enterprise(
    request: Request, db: CurrentSessionTransaction, body: CreateEnterpriseRequest
) -> ResponseModel:
    data = await workbench_domain_service.create_enterprise(
        db,
        user_id=request.user.id,
        name=body.name,
        slug=body.slug,
        description=body.description,
        join_policy=body.join_policy,
    )
    return response_base.success(data=data)


@router.get('/enterprises/search', dependencies=[DependsJwtAuth], summary='搜索企业')
async def search_enterprises(db: CurrentSession, q: str = '') -> ResponseModel:
    return response_base.success(data=await workbench_domain_service.search_enterprises(db, q=q))


@router.get('/enterprises/{enterprise_id}', dependencies=[DependsJwtAuth], summary='企业详情')
async def get_enterprise(db: CurrentSession, enterprise_id: int) -> ResponseModel:
    return response_base.success(data=await workbench_domain_service.get_enterprise(db, enterprise_id))


@router.patch('/enterprises/{enterprise_id}', dependencies=[DependsJwtAuth], summary='更新企业')
async def update_enterprise(db: CurrentSessionTransaction, enterprise_id: int, body: dict[str, Any]) -> ResponseModel:
    data = await workbench_domain_service.update_enterprise(db, enterprise_id=enterprise_id, updates=body)
    return response_base.success(data=data)


@router.delete('/enterprises/{enterprise_id}', dependencies=[DependsJwtAuth], summary='解散企业')
async def delete_enterprise(db: CurrentSessionTransaction, enterprise_id: int) -> ResponseModel:
    await workbench_domain_service.delete_enterprise(db, enterprise_id=enterprise_id)
    return response_base.success()


@router.get('/enterprises/{enterprise_id}/members', dependencies=[DependsJwtAuth], summary='企业成员')
async def list_members(db: CurrentSession, enterprise_id: int) -> ResponseModel:
    return response_base.success(data=await workbench_domain_service.list_members(db, enterprise_id=enterprise_id))


@router.post('/enterprises/{enterprise_id}/applications', dependencies=[DependsJwtAuth], summary='申请加入企业')
async def apply_enterprise(
    request: Request,
    db: CurrentSessionTransaction,
    enterprise_id: int,
    body: ApplyEnterpriseRequest,
) -> ResponseModel:
    data = await workbench_domain_service.apply_enterprise(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
        apply_message=body.apply_message,
        invite_code=body.invite_code,
    )
    return response_base.success(data=data)


@router.get('/enterprises/{enterprise_id}/applications', dependencies=[DependsJwtAuth], summary='企业申请列表')
async def list_applications(db: CurrentSession, enterprise_id: int, status: str = 'pending') -> ResponseModel:
    data = await workbench_domain_service.list_applications(db, enterprise_id=enterprise_id, status=status)
    return response_base.success(data=data)


@router.post(
    '/enterprises/{enterprise_id}/applications/{app_id}/approve', dependencies=[DependsJwtAuth], summary='通过申请'
)
async def approve_application(
    request: Request, db: CurrentSessionTransaction, enterprise_id: int, app_id: int
) -> ResponseModel:
    data = await workbench_domain_service.approve_application(
        db,
        enterprise_id=enterprise_id,
        app_id=app_id,
        decided_by=request.user.id,
    )
    return response_base.success(data=data)


@router.post(
    '/enterprises/{enterprise_id}/applications/{app_id}/reject', dependencies=[DependsJwtAuth], summary='拒绝申请'
)
async def reject_application(
    request: Request,
    db: CurrentSessionTransaction,
    enterprise_id: int,
    app_id: int,
    body: RejectApplicationRequest,
) -> ResponseModel:
    data = await workbench_domain_service.reject_application(
        db,
        enterprise_id=enterprise_id,
        app_id=app_id,
        decided_by=request.user.id,
        note=body.note,
    )
    return response_base.success(data=data)


@router.delete(
    '/enterprises/{enterprise_id}/members/{user_id}', dependencies=[DependsJwtAuth], summary='退出或移除成员'
)
async def remove_member(db: CurrentSessionTransaction, enterprise_id: int, user_id: int) -> ResponseModel:
    await workbench_domain_service.remove_member(db, enterprise_id=enterprise_id, user_id=user_id)
    return response_base.success()


@router.get('/enterprises/{enterprise_id}/invite-codes', dependencies=[DependsJwtAuth], summary='邀请码列表')
async def list_invite_codes(db: CurrentSession, enterprise_id: int) -> ResponseModel:
    return response_base.success(data=await workbench_domain_service.list_invite_codes(db, enterprise_id=enterprise_id))


@router.post('/enterprises/{enterprise_id}/invite-codes', dependencies=[DependsJwtAuth], summary='生成邀请码')
async def create_invite_code(
    request: Request,
    db: CurrentSessionTransaction,
    enterprise_id: int,
    body: CreateInviteCodeRequest,
) -> ResponseModel:
    data = await workbench_domain_service.create_invite_code(
        db,
        enterprise_id=enterprise_id,
        created_by=request.user.id,
        max_uses=body.max_uses,
        expires_at=body.expires_at,
        auto_approve=body.auto_approve,
    )
    return response_base.success(data=data)


@router.delete('/enterprises/{enterprise_id}/invite-codes/{code}', dependencies=[DependsJwtAuth], summary='撤销邀请码')
async def revoke_invite_code(db: CurrentSessionTransaction, enterprise_id: int, code: str) -> ResponseModel:
    data = await workbench_domain_service.revoke_invite_code(db, enterprise_id=enterprise_id, code=code)
    return response_base.success(data=data)
