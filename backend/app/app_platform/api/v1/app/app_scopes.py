"""应用权限定义表（{domain}.* namespace） - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_scopes import (
    CreateAppScopesParam,
    GetAppScopesDetail,
    UpdateAppScopesParam,
)
from backend.app.app_platform.service.app_scopes_service import app_scopes_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的应用权限定义表（{domain}.* namespace）列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_scopess(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppScopesDetail]]:
    page_data = await app_scopes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用权限定义表（{domain}.* namespace）',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_scopes(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppScopesParam,
) -> ResponseModel:
    result = await app_scopes_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取应用权限定义表（{domain}.* namespace）详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_scopes(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')],
) -> ResponseSchemaModel[GetAppScopesDetail]:
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    if app_scopes.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该应用权限定义表（{domain}.* namespace）')
    return response_base.success(data=app_scopes)


@router.put(
    '/{pk}',
    summary='更新应用权限定义表（{domain}.* namespace）',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_scopes(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')],
    obj: UpdateAppScopesParam,
) -> ResponseModel:
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    if getattr(app_scopes, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该应用权限定义表（{domain}.* namespace）')
    count = await app_scopes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除应用权限定义表（{domain}.* namespace）',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_scopes(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用权限定义表（{domain}.* namespace） ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_scopes = await app_scopes_service.get(db=db, pk=pk)
    if app_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用权限定义表（{domain}.* namespace）')
    from backend.app.app_platform.schema.app_scopes import DeleteAppScopesParam
    count = await app_scopes_service.delete(db=db, obj=DeleteAppScopesParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
