from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_account import (
    CreateHxCreatorAccountParam,
    DeleteHxCreatorAccountParam,
    GetHxCreatorAccountDetail,
    UpdateHxCreatorAccountParam,
)
from backend.app.creator.service.hx_creator_account_service import hx_creator_account_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取平台账号详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_account(
    db: CurrentSession, pk: Annotated[int, Path(description='平台账号 ID')]
) -> ResponseSchemaModel[GetHxCreatorAccountDetail]:
    hx_creator_account = await hx_creator_account_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_account)


@router.get(
    '',
    summary='分页获取所有平台账号',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_accounts_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorAccountDetail]]:
    page_data = await hx_creator_account_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建平台账号',
    dependencies=[
        Depends(RequestPermission('hx:creator:account:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_account(db: CurrentSessionTransaction, obj: CreateHxCreatorAccountParam) -> ResponseModel:
    await hx_creator_account_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新平台账号',
    dependencies=[
        Depends(RequestPermission('hx:creator:account:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_account(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='平台账号 ID')], obj: UpdateHxCreatorAccountParam
) -> ResponseModel:
    count = await hx_creator_account_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除平台账号',
    dependencies=[
        Depends(RequestPermission('hx:creator:account:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_accounts(db: CurrentSessionTransaction, obj: DeleteHxCreatorAccountParam) -> ResponseModel:
    count = await hx_creator_account_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
