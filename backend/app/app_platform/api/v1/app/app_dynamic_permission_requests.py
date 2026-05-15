"""动态权限请求 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_dynamic_permission_requests import (
    CreateAppDynamicPermissionRequestsParam,
    GetAppDynamicPermissionRequestsDetail,
    UpdateAppDynamicPermissionRequestsParam,
)
from backend.app.app_platform.service.app_dynamic_permission_requests_service import app_dynamic_permission_requests_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的动态权限请求列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_dynamic_permission_requestss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppDynamicPermissionRequestsDetail]]:
    page_data = await app_dynamic_permission_requests_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建动态权限请求',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_dynamic_permission_requests(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppDynamicPermissionRequestsParam,
) -> ResponseModel:
    result = await app_dynamic_permission_requests_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取动态权限请求详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_dynamic_permission_requests(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='动态权限请求 ID')],
) -> ResponseSchemaModel[GetAppDynamicPermissionRequestsDetail]:
    app_dynamic_permission_requests = await app_dynamic_permission_requests_service.get(db=db, pk=pk)
    if app_dynamic_permission_requests.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该动态权限请求')
    return response_base.success(data=app_dynamic_permission_requests)


@router.put(
    '/{pk}',
    summary='更新动态权限请求',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_dynamic_permission_requests(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='动态权限请求 ID')],
    obj: UpdateAppDynamicPermissionRequestsParam,
) -> ResponseModel:
    app_dynamic_permission_requests = await app_dynamic_permission_requests_service.get(db=db, pk=pk)
    if getattr(app_dynamic_permission_requests, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该动态权限请求')
    count = await app_dynamic_permission_requests_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除动态权限请求',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_dynamic_permission_requests(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='动态权限请求 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_dynamic_permission_requests = await app_dynamic_permission_requests_service.get(db=db, pk=pk)
    if app_dynamic_permission_requests.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该动态权限请求')
    from backend.app.app_platform.schema.app_dynamic_permission_requests import DeleteAppDynamicPermissionRequestsParam
    count = await app_dynamic_permission_requests_service.delete(db=db, obj=DeleteAppDynamicPermissionRequestsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
