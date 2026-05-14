"""平台权限定义表（hasn.* namespace） - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.app_platform.schema.platform_scopes import (
    CreatePlatformScopesParam,
    UpdatePlatformScopesParam,
)
from backend.app.app_platform.service.platform_scopes_service import platform_scopes_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='平台权限定义表（hasn.* namespace）列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_platform_scopess(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await platform_scopes_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建平台权限定义表（hasn.* namespace）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_platform_scopes(
    db: CurrentSessionTransaction,
    obj: CreatePlatformScopesParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await platform_scopes_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取平台权限定义表（hasn.* namespace）详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_platform_scopes(
    db: CurrentSession,
    pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    if platform_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该平台权限定义表（hasn.* namespace）')
    return response_base.success(data=platform_scopes)


@router.put(
    '/{pk}',
    summary='更新平台权限定义表（hasn.* namespace）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_platform_scopes(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')],
    obj: UpdatePlatformScopesParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    if platform_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该平台权限定义表（hasn.* namespace）')
    count = await platform_scopes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除平台权限定义表（hasn.* namespace）',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_platform_scopes(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    if platform_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该平台权限定义表（hasn.* namespace）')
    from backend.app.app_platform.schema.platform_scopes import DeletePlatformScopesParam
    count = await platform_scopes_service.delete(db=db, obj=DeletePlatformScopesParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
