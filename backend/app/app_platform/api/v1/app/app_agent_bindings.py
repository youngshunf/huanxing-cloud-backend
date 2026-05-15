"""Installation 绑定的 Agent 列 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_agent_bindings import (
    CreateAppAgentBindingsParam,
    GetAppAgentBindingsDetail,
    UpdateAppAgentBindingsParam,
)
from backend.app.app_platform.service.app_agent_bindings_service import app_agent_bindings_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的Installation 绑定的 Agent 列列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_agent_bindingss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppAgentBindingsDetail]]:
    page_data = await app_agent_bindings_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建Installation 绑定的 Agent 列',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_agent_bindings(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppAgentBindingsParam,
) -> ResponseModel:
    result = await app_agent_bindings_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取Installation 绑定的 Agent 列详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_agent_bindings(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')],
) -> ResponseSchemaModel[GetAppAgentBindingsDetail]:
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    if app_agent_bindings.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该Installation 绑定的 Agent 列')
    return response_base.success(data=app_agent_bindings)


@router.put(
    '/{pk}',
    summary='更新Installation 绑定的 Agent 列',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_agent_bindings(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')],
    obj: UpdateAppAgentBindingsParam,
) -> ResponseModel:
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    if getattr(app_agent_bindings, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该Installation 绑定的 Agent 列')
    count = await app_agent_bindings_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除Installation 绑定的 Agent 列',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_agent_bindings(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    if app_agent_bindings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该Installation 绑定的 Agent 列')
    from backend.app.app_platform.schema.app_agent_bindings import DeleteAppAgentBindingsParam
    count = await app_agent_bindings_service.delete(db=db, obj=DeleteAppAgentBindingsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
