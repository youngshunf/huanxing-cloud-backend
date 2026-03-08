"""HASN 用户管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_core.schema.admin.hasn_humans import (
    CreateHasnHumanParam,
    DeleteHasnHumanParam,
    GetHasnHumanDetail,
    UpdateHasnHumanParam,
)
from backend.app.hasn_core.service.admin.hasn_humans import hasn_humans_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取用户详情', dependencies=[DependsJwtAuth])
async def get_hasn_humans(
    db: CurrentSession, pk: Annotated[str, Path(description='用户 ID')]
) -> ResponseSchemaModel[GetHasnHumanDetail]:
    obj = await hasn_humans_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取用户列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_humans_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnHumanDetail]]:
    page_data = await hasn_humans_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建用户',
    dependencies=[Depends(RequestPermission('hasn:humans:add')), DependsRBAC],
)
async def create_hasn_humans(db: CurrentSessionTransaction, obj: CreateHasnHumanParam) -> ResponseModel:
    await hasn_humans_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新用户',
    dependencies=[Depends(RequestPermission('hasn:humans:edit')), DependsRBAC],
)
async def update_hasn_humans(
    db: CurrentSessionTransaction,
    pk: Annotated[str, Path(description='用户 ID')],
    obj: UpdateHasnHumanParam,
) -> ResponseModel:
    count = await hasn_humans_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除用户',
    dependencies=[Depends(RequestPermission('hasn:humans:del')), DependsRBAC],
)
async def delete_hasn_humans(db: CurrentSessionTransaction, obj: DeleteHasnHumanParam) -> ResponseModel:
    count = await hasn_humans_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
