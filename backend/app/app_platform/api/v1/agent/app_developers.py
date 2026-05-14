"""应用开发者 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.app_platform.schema.app_developers import (
    CreateAppDevelopersParam,
    UpdateAppDevelopersParam,
)
from backend.app.app_platform.service.app_developers_service import app_developers_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='应用开发者列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_developerss(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await app_developers_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建应用开发者',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_developers(
    db: CurrentSessionTransaction,
    obj: CreateAppDevelopersParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await app_developers_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取应用开发者详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_developers(
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用开发者 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_developers = await app_developers_service.get(db=db, pk=pk)
    if app_developers.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该应用开发者')
    return response_base.success(data=app_developers)


@router.put(
    '/{pk}',
    summary='更新应用开发者',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_developers(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用开发者 ID')],
    obj: UpdateAppDevelopersParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_developers = await app_developers_service.get(db=db, pk=pk)
    if app_developers.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该应用开发者')
    count = await app_developers_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除应用开发者',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_developers(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用开发者 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_developers = await app_developers_service.get(db=db, pk=pk)
    if app_developers.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用开发者')
    from backend.app.app_platform.schema.app_developers import DeleteAppDevelopersParam
    count = await app_developers_service.delete(db=db, obj=DeleteAppDevelopersParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
