"""用户第三方应用凭证 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.integration.schema.integration_credentials import (
    CreateIntegrationCredentialsParam,
    GetIntegrationCredentialsDetail,
    UpdateIntegrationCredentialsParam,
)
from backend.app.integration.service.integration_credentials_service import integration_credentials_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的用户第三方应用凭证列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_integration_credentials',
)
async def get_my_integration_credentials(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetIntegrationCredentialsDetail]]:
    page_data = await integration_credentials_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建用户第三方应用凭证',
    dependencies=[DependsJwtAuth],
    name='app_create_my_integration_credentials',
)
async def create_my_integration_credentials(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateIntegrationCredentialsParam,
) -> ResponseModel:
    result = await integration_credentials_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取用户第三方应用凭证详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_integration_credentials_detail',
)
async def get_my_integration_credentials_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='用户第三方应用凭证 ID')],
) -> ResponseSchemaModel[GetIntegrationCredentialsDetail]:
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    if integration_credentials.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该用户第三方应用凭证')
    return response_base.success(data=integration_credentials)


@router.put(
    '/{pk}',
    summary='更新用户第三方应用凭证',
    dependencies=[DependsJwtAuth],
    name='app_update_my_integration_credentials',
)
async def update_my_integration_credentials(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='用户第三方应用凭证 ID')],
    obj: UpdateIntegrationCredentialsParam,
) -> ResponseModel:
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    if getattr(integration_credentials, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该用户第三方应用凭证')
    count = await integration_credentials_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除用户第三方应用凭证',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_integration_credentials',
)
async def delete_my_integration_credentials(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='用户第三方应用凭证 ID')],
) -> ResponseModel:
    user_id = request.user.id
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    if integration_credentials.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该用户第三方应用凭证')
    from backend.app.integration.schema.integration_credentials import DeleteIntegrationCredentialsParam
    count = await integration_credentials_service.delete(db=db, obj=DeleteIntegrationCredentialsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
