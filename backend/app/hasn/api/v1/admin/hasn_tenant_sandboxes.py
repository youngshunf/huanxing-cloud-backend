from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_tenant_sandboxes import (
    CreateHasnTenantSandboxesParam,
    DeleteHasnTenantSandboxesParam,
    GetHasnTenantSandboxesDetail,
    UpdateHasnTenantSandboxesParam,
)
from backend.app.hasn.service.hasn_tenant_sandboxes_service import hasn_tenant_sandboxes_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取HASN Tenant Sandbox lifecycle 详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_tenant_sandboxes')
async def get_hasn_tenant_sandboxes(
    db: CurrentSession, pk: Annotated[int, Path(description='HASN Tenant Sandbox lifecycle  ID')]
) -> ResponseSchemaModel[GetHasnTenantSandboxesDetail]:
    hasn_tenant_sandboxes = await hasn_tenant_sandboxes_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_tenant_sandboxes)


@router.get(
    '',
    summary='分页获取所有HASN Tenant Sandbox lifecycle ',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_hasn_tenant_sandboxess_paginated')
async def get_hasn_tenant_sandboxess_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnTenantSandboxesDetail]]:
    page_data = await hasn_tenant_sandboxes_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN Tenant Sandbox lifecycle ',
    dependencies=[
        Depends(RequestPermission('hasn:tenant:sandboxes:add')),
        DependsRBAC,
    ],
)
async def create_hasn_tenant_sandboxes(db: CurrentSessionTransaction, obj: CreateHasnTenantSandboxesParam) -> ResponseModel:
    await hasn_tenant_sandboxes_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新HASN Tenant Sandbox lifecycle ',
    dependencies=[
        Depends(RequestPermission('hasn:tenant:sandboxes:edit')),
        DependsRBAC,
    ],
)
async def update_hasn_tenant_sandboxes(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='HASN Tenant Sandbox lifecycle  ID')], obj: UpdateHasnTenantSandboxesParam
) -> ResponseModel:
    count = await hasn_tenant_sandboxes_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除HASN Tenant Sandbox lifecycle ',
    dependencies=[
        Depends(RequestPermission('hasn:tenant:sandboxes:del')),
        DependsRBAC,
    ],
)
async def delete_hasn_tenant_sandboxess(db: CurrentSessionTransaction, obj: DeleteHasnTenantSandboxesParam) -> ResponseModel:
    count = await hasn_tenant_sandboxes_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
