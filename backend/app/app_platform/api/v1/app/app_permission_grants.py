"""权限授予记录 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_permission_grants import (
    CreateAppPermissionGrantsParam,
    GetAppPermissionGrantsDetail,
    UpdateAppPermissionGrantsParam,
)
from backend.app.app_platform.service.app_permission_grants_service import app_permission_grants_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的权限授予记录列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_permission_grantss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppPermissionGrantsDetail]]:
    page_data = await app_permission_grants_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建权限授予记录',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_permission_grants(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppPermissionGrantsParam,
) -> ResponseModel:
    result = await app_permission_grants_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取权限授予记录详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_permission_grants(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='权限授予记录 ID')],
) -> ResponseSchemaModel[GetAppPermissionGrantsDetail]:
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    if app_permission_grants.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该权限授予记录')
    return response_base.success(data=app_permission_grants)


@router.put(
    '/{pk}',
    summary='更新权限授予记录',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_permission_grants(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='权限授予记录 ID')],
    obj: UpdateAppPermissionGrantsParam,
) -> ResponseModel:
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    if getattr(app_permission_grants, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该权限授予记录')
    count = await app_permission_grants_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除权限授予记录',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_permission_grants(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='权限授予记录 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_permission_grants = await app_permission_grants_service.get(db=db, pk=pk)
    if app_permission_grants.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该权限授予记录')
    from backend.app.app_platform.schema.app_permission_grants import DeleteAppPermissionGrantsParam
    count = await app_permission_grants_service.delete(db=db, obj=DeleteAppPermissionGrantsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
