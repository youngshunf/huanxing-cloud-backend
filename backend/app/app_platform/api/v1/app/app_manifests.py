"""App 清单 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_manifests import (
    CreateAppManifestsParam,
    GetAppManifestsDetail,
    UpdateAppManifestsParam,
)
from backend.app.app_platform.service.app_manifests_service import app_manifests_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的App 清单列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_manifestss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppManifestsDetail]]:
    page_data = await app_manifests_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 清单',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_manifests(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppManifestsParam,
) -> ResponseModel:
    result = await app_manifests_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取App 清单详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_manifests(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 清单 ID')],
) -> ResponseSchemaModel[GetAppManifestsDetail]:
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    if app_manifests.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该App 清单')
    return response_base.success(data=app_manifests)


@router.put(
    '/{pk}',
    summary='更新App 清单',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_manifests(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 清单 ID')],
    obj: UpdateAppManifestsParam,
) -> ResponseModel:
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    if getattr(app_manifests, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该App 清单')
    count = await app_manifests_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除App 清单',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_manifests(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 清单 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_manifests = await app_manifests_service.get(db=db, pk=pk)
    if app_manifests.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App 清单')
    from backend.app.app_platform.schema.app_manifests import DeleteAppManifestsParam
    count = await app_manifests_service.delete(db=db, obj=DeleteAppManifestsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
