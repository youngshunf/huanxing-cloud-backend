from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn.schema.hasn_contact_requests import (
    CreateHasnContactRequestsParam,
    DeleteHasnContactRequestsParam,
    GetHasnContactRequestsDetail,
    UpdateHasnContactRequestsParam,
)
from backend.app.hasn.service.hasn_contact_requests_service import hasn_contact_requests_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '/{pk}',
    summary='获取HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）详情',
    dependencies=[DependsJwtAuth],
    name='admin_get_hasn_contact_requests',
)
async def get_hasn_contact_requests(
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID')],
) -> ResponseSchemaModel[GetHasnContactRequestsDetail]:
    hasn_contact_requests = await hasn_contact_requests_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_contact_requests)


@router.get(
    '',
    summary='分页获取所有HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_contact_requests_paginated',
)
async def get_hasn_contact_requests_paginated(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnContactRequestsDetail]]:
    page_data = await hasn_contact_requests_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）',
    dependencies=[
        Depends(RequestPermission('hasn:contact:requests:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_contact_requests',
)
async def create_hasn_contact_requests(
    db: CurrentSessionTransaction, obj: CreateHasnContactRequestsParam
) -> ResponseModel:
    await hasn_contact_requests_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）',
    dependencies=[
        Depends(RequestPermission('hasn:contact:requests:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_contact_requests',
)
async def update_hasn_contact_requests(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表） ID')],
    obj: UpdateHasnContactRequestsParam,
) -> ResponseModel:
    count = await hasn_contact_requests_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除HASN 好友请求表（请求生命周期独立于 hasn_contacts 关系表）',
    dependencies=[
        Depends(RequestPermission('hasn:contact:requests:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_contact_requests',
)
async def delete_hasn_contact_requests(
    db: CurrentSessionTransaction, obj: DeleteHasnContactRequestsParam
) -> ResponseModel:
    count = await hasn_contact_requests_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
