"""平台权限定义表（hasn.* namespace） - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.platform_scopes import (
    CreatePlatformScopesParam,
    GetPlatformScopesDetail,
    UpdatePlatformScopesParam,
)
from backend.app.app_platform.service.platform_scopes_service import platform_scopes_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的平台权限定义表（hasn.* namespace）列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_platform_scopess(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetPlatformScopesDetail]]:
    page_data = await platform_scopes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建平台权限定义表（hasn.* namespace）',
    dependencies=[DependsJwtAuth],
)
async def create_my_platform_scopes(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreatePlatformScopesParam,
) -> ResponseModel:
    result = await platform_scopes_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取平台权限定义表（hasn.* namespace）详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_platform_scopes(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')],
) -> ResponseSchemaModel[GetPlatformScopesDetail]:
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    if platform_scopes.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该平台权限定义表（hasn.* namespace）')
    return response_base.success(data=platform_scopes)


@router.put(
    '/{pk}',
    summary='更新平台权限定义表（hasn.* namespace）',
    dependencies=[DependsJwtAuth],
)
async def update_my_platform_scopes(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')],
    obj: UpdatePlatformScopesParam,
) -> ResponseModel:
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    if getattr(platform_scopes, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该平台权限定义表（hasn.* namespace）')
    count = await platform_scopes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除平台权限定义表（hasn.* namespace）',
    dependencies=[DependsJwtAuth],
)
async def delete_my_platform_scopes(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='平台权限定义表（hasn.* namespace） ID')],
) -> ResponseModel:
    user_id = request.user.id
    platform_scopes = await platform_scopes_service.get(db=db, pk=pk)
    if platform_scopes.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该平台权限定义表（hasn.* namespace）')
    from backend.app.app_platform.schema.platform_scopes import DeletePlatformScopesParam
    count = await platform_scopes_service.delete(db=db, obj=DeletePlatformScopesParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
