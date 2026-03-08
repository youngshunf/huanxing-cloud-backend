"""HASN 联系人管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_social.schema.admin.hasn_contacts import (
    CreateHasnContactParam,
    DeleteHasnContactParam,
    GetHasnContactDetail,
    UpdateHasnContactParam,
)
from backend.app.hasn_social.service.admin.hasn_contacts import hasn_contacts_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取联系人详情', dependencies=[DependsJwtAuth])
async def get_hasn_contacts(
    db: CurrentSession, pk: Annotated[int, Path(description='联系人 ID')]
) -> ResponseSchemaModel[GetHasnContactDetail]:
    obj = await hasn_contacts_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取联系人列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_contacts_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnContactDetail]]:
    page_data = await hasn_contacts_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建联系人',
    dependencies=[Depends(RequestPermission('hasn:contacts:add')), DependsRBAC],
)
async def create_hasn_contacts(db: CurrentSessionTransaction, obj: CreateHasnContactParam) -> ResponseModel:
    await hasn_contacts_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新联系人',
    dependencies=[Depends(RequestPermission('hasn:contacts:edit')), DependsRBAC],
)
async def update_hasn_contacts(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='联系人 ID')],
    obj: UpdateHasnContactParam,
) -> ResponseModel:
    count = await hasn_contacts_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除联系人',
    dependencies=[Depends(RequestPermission('hasn:contacts:del')), DependsRBAC],
)
async def delete_hasn_contacts(db: CurrentSessionTransaction, obj: DeleteHasnContactParam) -> ResponseModel:
    count = await hasn_contacts_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
