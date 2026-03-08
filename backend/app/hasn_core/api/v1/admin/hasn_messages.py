"""HASN 消息管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_core.schema.admin.hasn_messages import (
    CreateHasnMessageParam,
    DeleteHasnMessageParam,
    GetHasnMessageDetail,
    UpdateHasnMessageParam,
)
from backend.app.hasn_core.service.admin.hasn_messages import hasn_messages_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取消息详情', dependencies=[DependsJwtAuth])
async def get_hasn_messages(
    db: CurrentSession, pk: Annotated[int, Path(description='消息 ID')]
) -> ResponseSchemaModel[GetHasnMessageDetail]:
    obj = await hasn_messages_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取消息列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_messages_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnMessageDetail]]:
    page_data = await hasn_messages_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建消息',
    dependencies=[Depends(RequestPermission('hasn:messages:add')), DependsRBAC],
)
async def create_hasn_messages(db: CurrentSessionTransaction, obj: CreateHasnMessageParam) -> ResponseModel:
    await hasn_messages_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新消息',
    dependencies=[Depends(RequestPermission('hasn:messages:edit')), DependsRBAC],
)
async def update_hasn_messages(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='消息 ID')],
    obj: UpdateHasnMessageParam,
) -> ResponseModel:
    count = await hasn_messages_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除消息',
    dependencies=[Depends(RequestPermission('hasn:messages:del')), DependsRBAC],
)
async def delete_hasn_messages(db: CurrentSessionTransaction, obj: DeleteHasnMessageParam) -> ResponseModel:
    count = await hasn_messages_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
