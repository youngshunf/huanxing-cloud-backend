"""App 清单 - Agent API

认证方式: DependsAgentJwtAuth（X-Agent-Key）
用户身份: 通过 X-User-Id Header 传入 sys_user.uuid
"""
from typing import Annotated

from fastapi import APIRouter, Header, Path

from backend.app.app_platform.schema.app_manifests import (
    CreateAppManifestsParam,
    UpdateAppManifestsParam,
)
from backend.app.app_platform.service.app_manifests_service import app_manifests_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.common.security.agent_utils import resolve_user_id
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='App 清单列表',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_list_app_manifestss(
    db: CurrentSession,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    data = await app_manifests_service.get_list(db=db)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建App 清单',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_create_app_manifests(
    db: CurrentSessionTransaction,
    obj: CreateAppManifestsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    result = await app_manifests_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取App 清单详情',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_get_app_manifests(
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 清单 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    if app_manifests.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该App 清单')
    return response_base.success(data=app_manifests)


@router.put(
    '/{pk}',
    summary='更新App 清单',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_update_app_manifests(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 清单 ID')],
    obj: UpdateAppManifestsParam,
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    if app_manifests.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该App 清单')
    count = await app_manifests_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除App 清单',
    dependencies=[DependsAgentJwtAuth],
)
async def agent_delete_app_manifests(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 清单 ID')],
    x_user_id: Annotated[str, Header(description='用户 UUID')],
) -> ResponseModel:
    user_id = await resolve_user_id(db, x_user_id)
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    if app_manifests.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App 清单')
    from backend.app.app_platform.schema.app_manifests import DeleteAppManifestsParam
    count = await app_manifests_service.delete(db=db, obj=DeleteAppManifestsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
