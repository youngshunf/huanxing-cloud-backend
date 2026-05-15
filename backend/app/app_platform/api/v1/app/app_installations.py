"""App 安装记录 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_installations import (
    CreateAppInstallationsParam,
    GetAppInstallationsDetail,
    UpdateAppInstallationsParam,
)
from backend.app.app_platform.service.app_installations_service import app_installations_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的App 安装记录列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_installationss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppInstallationsDetail]]:
    page_data = await app_installations_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 安装记录',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_installations(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppInstallationsParam,
) -> ResponseModel:
    result = await app_installations_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取App 安装记录详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_installations(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 安装记录 ID')],
) -> ResponseSchemaModel[GetAppInstallationsDetail]:
    app_installations = await app_installations_service.get(db=db, pk=pk)
    if app_installations.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该App 安装记录')
    return response_base.success(data=app_installations)


@router.put(
    '/{pk}',
    summary='更新App 安装记录',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_installations(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 安装记录 ID')],
    obj: UpdateAppInstallationsParam,
) -> ResponseModel:
    app_installations = await app_installations_service.get(db=db, pk=pk)
    if getattr(app_installations, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该App 安装记录')
    count = await app_installations_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除App 安装记录',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_installations(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 安装记录 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_installations = await app_installations_service.get(db=db, pk=pk)
    if app_installations.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App 安装记录')
    from backend.app.app_platform.schema.app_installations import DeleteAppInstallationsParam
    count = await app_installations_service.delete(db=db, obj=DeleteAppInstallationsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
