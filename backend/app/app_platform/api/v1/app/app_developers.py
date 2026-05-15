"""应用开发者 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_developers import (
    CreateAppDevelopersParam,
    GetAppDevelopersDetail,
    UpdateAppDevelopersParam,
)
from backend.app.app_platform.service.app_developers_service import app_developers_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的应用开发者列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_developerss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppDevelopersDetail]]:
    page_data = await app_developers_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用开发者',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_developers(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppDevelopersParam,
) -> ResponseModel:
    result = await app_developers_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取应用开发者详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_developers(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用开发者 ID')],
) -> ResponseSchemaModel[GetAppDevelopersDetail]:
    app_developers = await app_developers_service.get(db=db, pk=pk)
    if app_developers.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该应用开发者')
    return response_base.success(data=app_developers)


@router.put(
    '/{pk}',
    summary='更新应用开发者',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_developers(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用开发者 ID')],
    obj: UpdateAppDevelopersParam,
) -> ResponseModel:
    app_developers = await app_developers_service.get(db=db, pk=pk)
    if getattr(app_developers, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该应用开发者')
    count = await app_developers_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除应用开发者',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_developers(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用开发者 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_developers = await app_developers_service.get(db=db, pk=pk)
    if app_developers.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用开发者')
    from backend.app.app_platform.schema.app_developers import DeleteAppDevelopersParam
    count = await app_developers_service.delete(db=db, obj=DeleteAppDevelopersParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
