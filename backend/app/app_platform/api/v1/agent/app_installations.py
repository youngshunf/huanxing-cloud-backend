"""App 安装记录 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.app_platform.schema.app_installations import (
    CreateAppInstallationsParam,
    UpdateAppInstallationsParam,
)
from backend.app.app_platform.service.app_installations_service import app_installations_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='App 安装记录列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_installationss(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await app_installations_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建App 安装记录',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_installations(
    db: CurrentSessionTransaction,
    obj: CreateAppInstallationsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await app_installations_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取App 安装记录详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_installations(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 安装记录 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_installations = await app_installations_service.get(db=db, pk=pk)
    if app_installations.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该App 安装记录')
    return response_base.success(data=app_installations)


@router.put(
    '/{pk}',
    summary='更新App 安装记录',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_installations(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 安装记录 ID')],
    obj: UpdateAppInstallationsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_installations = await app_installations_service.get(db=db, pk=pk)
    if app_installations.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该App 安装记录')
    count = await app_installations_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除App 安装记录',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_installations(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 安装记录 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_installations = await app_installations_service.get(db=db, pk=pk)
    if app_installations.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App 安装记录')
    from backend.app.app_platform.schema.app_installations import DeleteAppInstallationsParam
    count = await app_installations_service.delete(db=db, obj=DeleteAppInstallationsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
