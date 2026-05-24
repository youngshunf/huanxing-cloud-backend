"""HASN 会话产物 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_session_artifacts import (
    CreateHasnSessionArtifactsParam,
    GetHasnSessionArtifactsDetail,
    UpdateHasnSessionArtifactsParam,
)
from backend.app.hasn.service.hasn_session_artifacts_service import hasn_session_artifacts_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的HASN 会话产物列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_hasn_session_artifacts',
)
async def get_my_hasn_session_artifacts(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnSessionArtifactsDetail]]:
    page_data = await hasn_session_artifacts_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN 会话产物',
    dependencies=[DependsJwtAuth],
    name='app_create_my_hasn_session_artifacts',
)
async def create_my_hasn_session_artifacts(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnSessionArtifactsParam,
) -> ResponseModel:
    result = await hasn_session_artifacts_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN 会话产物详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_hasn_session_artifacts_detail',
)
async def get_my_hasn_session_artifacts_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 会话产物 ID')],
) -> ResponseSchemaModel[GetHasnSessionArtifactsDetail]:
    hasn_session_artifacts = await hasn_session_artifacts_service.get(db=db, pk=pk)
    if hasn_session_artifacts.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该HASN 会话产物')
    return response_base.success(data=hasn_session_artifacts)


@router.put(
    '/{pk}',
    summary='更新HASN 会话产物',
    dependencies=[DependsJwtAuth],
    name='app_update_my_hasn_session_artifacts',
)
async def update_my_hasn_session_artifacts(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 会话产物 ID')],
    obj: UpdateHasnSessionArtifactsParam,
) -> ResponseModel:
    hasn_session_artifacts = await hasn_session_artifacts_service.get(db=db, pk=pk)
    if getattr(hasn_session_artifacts, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该HASN 会话产物')
    count = await hasn_session_artifacts_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN 会话产物',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_hasn_session_artifacts',
)
async def delete_my_hasn_session_artifacts(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 会话产物 ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_session_artifacts = await hasn_session_artifacts_service.get(db=db, pk=pk)
    if hasn_session_artifacts.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN 会话产物')
    from backend.app.hasn.schema.hasn_session_artifacts import DeleteHasnSessionArtifactsParam
    count = await hasn_session_artifacts_service.delete(db=db, obj=DeleteHasnSessionArtifactsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
