"""HASN 群成员管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_core.schema.admin.hasn_group_members import (
    CreateHasnGroupMemberParam,
    DeleteHasnGroupMemberParam,
    GetHasnGroupMemberDetail,
    UpdateHasnGroupMemberParam,
)
from backend.app.hasn_core.service.admin.hasn_group_members import hasn_group_members_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取群成员详情', dependencies=[DependsJwtAuth])
async def get_hasn_group_members(
    db: CurrentSession, pk: Annotated[int, Path(description='群成员 ID')]
) -> ResponseSchemaModel[GetHasnGroupMemberDetail]:
    obj = await hasn_group_members_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取群成员列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_group_members_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnGroupMemberDetail]]:
    page_data = await hasn_group_members_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建群成员',
    dependencies=[Depends(RequestPermission('hasn:group:members:add')), DependsRBAC],
)
async def create_hasn_group_members(db: CurrentSessionTransaction, obj: CreateHasnGroupMemberParam) -> ResponseModel:
    await hasn_group_members_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新群成员',
    dependencies=[Depends(RequestPermission('hasn:group:members:edit')), DependsRBAC],
)
async def update_hasn_group_members(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='群成员 ID')],
    obj: UpdateHasnGroupMemberParam,
) -> ResponseModel:
    count = await hasn_group_members_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除群成员',
    dependencies=[Depends(RequestPermission('hasn:group:members:del')), DependsRBAC],
)
async def delete_hasn_group_members(db: CurrentSessionTransaction, obj: DeleteHasnGroupMemberParam) -> ResponseModel:
    count = await hasn_group_members_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
