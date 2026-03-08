"""HASN 通知管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_core.schema.admin.hasn_notifications import (
    CreateHasnNotificationParam,
    DeleteHasnNotificationParam,
    GetHasnNotificationDetail,
    UpdateHasnNotificationParam,
)
from backend.app.hasn_core.service.admin.hasn_notifications import hasn_notifications_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取通知详情', dependencies=[DependsJwtAuth])
async def get_hasn_notifications(
    db: CurrentSession, pk: Annotated[int, Path(description='通知 ID')]
) -> ResponseSchemaModel[GetHasnNotificationDetail]:
    obj = await hasn_notifications_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取通知列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_notifications_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnNotificationDetail]]:
    page_data = await hasn_notifications_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建通知',
    dependencies=[Depends(RequestPermission('hasn:notifications:add')), DependsRBAC],
)
async def create_hasn_notifications(db: CurrentSessionTransaction, obj: CreateHasnNotificationParam) -> ResponseModel:
    await hasn_notifications_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新通知',
    dependencies=[Depends(RequestPermission('hasn:notifications:edit')), DependsRBAC],
)
async def update_hasn_notifications(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='通知 ID')],
    obj: UpdateHasnNotificationParam,
) -> ResponseModel:
    count = await hasn_notifications_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除通知',
    dependencies=[Depends(RequestPermission('hasn:notifications:del')), DependsRBAC],
)
async def delete_hasn_notifications(db: CurrentSessionTransaction, obj: DeleteHasnNotificationParam) -> ResponseModel:
    count = await hasn_notifications_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
