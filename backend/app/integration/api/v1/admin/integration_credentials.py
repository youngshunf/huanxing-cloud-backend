from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.integration.schema.integration_credentials import (
    CreateIntegrationCredentialsParam,
    DeleteIntegrationCredentialsParam,
    GetIntegrationCredentialsDetail,
    UpdateIntegrationCredentialsParam,
)
from backend.app.integration.service.integration_credentials_service import integration_credentials_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取用户第三方应用凭证详情', dependencies=[DependsJwtAuth], name='admin_get_integration_credentials')
async def get_integration_credentials(
    db: CurrentSession, pk: Annotated[int, Path(description='用户第三方应用凭证 ID')]
) -> ResponseSchemaModel[GetIntegrationCredentialsDetail]:
    integration_credentials = await integration_credentials_service.get(db=db, pk=pk)
    return response_base.success(data=integration_credentials)


@router.get(
    '',
    summary='分页获取所有用户第三方应用凭证',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_integration_credentials_paginated',
)
async def get_integration_credentials_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetIntegrationCredentialsDetail]]:
    page_data = await integration_credentials_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建用户第三方应用凭证',
    dependencies=[
        Depends(RequestPermission('integration:credentials:add')),
        DependsRBAC,
    ],
    name='admin_create_integration_credentials',
)
async def create_integration_credentials(db: CurrentSessionTransaction, obj: CreateIntegrationCredentialsParam) -> ResponseModel:
    await integration_credentials_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新用户第三方应用凭证',
    dependencies=[
        Depends(RequestPermission('integration:credentials:edit')),
        DependsRBAC,
    ],
    name='admin_update_integration_credentials',
)
async def update_integration_credentials(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='用户第三方应用凭证 ID')], obj: UpdateIntegrationCredentialsParam
) -> ResponseModel:
    count = await integration_credentials_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除用户第三方应用凭证',
    dependencies=[
        Depends(RequestPermission('integration:credentials:del')),
        DependsRBAC,
    ],
    name='admin_delete_integration_credentials',
)
async def delete_integration_credentials(db: CurrentSessionTransaction, obj: DeleteIntegrationCredentialsParam) -> ResponseModel:
    count = await integration_credentials_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
