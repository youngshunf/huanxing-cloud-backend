"""Admin API — 支付应用管理"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.huanxing.schema.pay_app import (
    CreatePayAppParam,
    DeletePayAppParam,
    GetPayAppDetail,
    UpdatePayAppParam,
)
from backend.app.huanxing.service.pay_app_service import pay_app_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取支付应用详情', dependencies=[DependsJwtAuth])
async def get_pay_app(
    db: CurrentSession, pk: Annotated[int, Path(description='支付应用 ID')]
) -> ResponseSchemaModel[GetPayAppDetail]:
    pay_app = await pay_app_service.get(db=db, pk=pk)
    return response_base.success(data=pay_app)


@router.get(
    '',
    summary='分页获取所有支付应用',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_pay_apps_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetPayAppDetail]]:
    page_data = await pay_app_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建支付应用',
    dependencies=[
        Depends(RequestPermission('huanxing:pay:add')),
        DependsRBAC,
    ],
)
async def create_pay_app(db: CurrentSessionTransaction, obj: CreatePayAppParam) -> ResponseModel:
    await pay_app_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新支付应用',
    dependencies=[
        Depends(RequestPermission('huanxing:pay:edit')),
        DependsRBAC,
    ],
)
async def update_pay_app(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='支付应用 ID')],
    obj: UpdatePayAppParam,
) -> ResponseModel:
    count = await pay_app_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除支付应用',
    dependencies=[
        Depends(RequestPermission('huanxing:pay:del')),
        DependsRBAC,
    ],
)
async def delete_pay_apps(db: CurrentSessionTransaction, obj: DeletePayAppParam) -> ResponseModel:
    count = await pay_app_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
