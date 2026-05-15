"""App 购买凭证 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_entitlements import (
    CreateAppEntitlementsParam,
    GetAppEntitlementsDetail,
    UpdateAppEntitlementsParam,
)
from backend.app.app_platform.service.app_entitlements_service import app_entitlements_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的App 购买凭证列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_entitlementss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppEntitlementsDetail]]:
    page_data = await app_entitlements_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App 购买凭证',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_entitlements(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppEntitlementsParam,
) -> ResponseModel:
    result = await app_entitlements_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取App 购买凭证详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_entitlements(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='App 购买凭证 ID')],
) -> ResponseSchemaModel[GetAppEntitlementsDetail]:
    app_entitlements = await app_entitlements_service.get(db=db, pk=pk)
    if app_entitlements.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该App 购买凭证')
    return response_base.success(data=app_entitlements)


@router.put(
    '/{pk}',
    summary='更新App 购买凭证',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_entitlements(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 购买凭证 ID')],
    obj: UpdateAppEntitlementsParam,
) -> ResponseModel:
    app_entitlements = await app_entitlements_service.get(db=db, pk=pk)
    if getattr(app_entitlements, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该App 购买凭证')
    count = await app_entitlements_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除App 购买凭证',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_entitlements(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App 购买凭证 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_entitlements = await app_entitlements_service.get(db=db, pk=pk)
    if app_entitlements.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App 购买凭证')
    from backend.app.app_platform.schema.app_entitlements import DeleteAppEntitlementsParam
    count = await app_entitlements_service.delete(db=db, obj=DeleteAppEntitlementsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
