from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.huanxing.schema.huanxing_user import (
    CreateHuanxingUserParam,
    DeleteHuanxingUserParam,
    GetHuanxingUserDetail,
    UpdateHuanxingUserParam,
)
from backend.app.huanxing.service.huanxing_user_service import huanxing_user_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取唤星用户详情', dependencies=[DependsJwtAuth])
async def get_huanxing_user(
    db: CurrentSession, pk: Annotated[int, Path(description='唤星用户 ID')]
) -> ResponseSchemaModel[GetHuanxingUserDetail]:
    huanxing_user = await huanxing_user_service.get(db=db, pk=pk)
    return response_base.success(data=huanxing_user)


@router.get(
    '',
    summary='分页获取所有唤星用户',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_huanxing_users_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHuanxingUserDetail]]:
    page_data = await huanxing_user_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建唤星用户',
    dependencies=[
        Depends(RequestPermission('huanxing:user:add')),
        DependsRBAC,
    ],
)
async def create_huanxing_user(db: CurrentSessionTransaction, obj: CreateHuanxingUserParam) -> ResponseModel:
    await huanxing_user_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新唤星用户',
    dependencies=[
        Depends(RequestPermission('huanxing:user:edit')),
        DependsRBAC,
    ],
)
async def update_huanxing_user(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='唤星用户 ID')], obj: UpdateHuanxingUserParam
) -> ResponseModel:
    count = await huanxing_user_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除唤星用户',
    dependencies=[
        Depends(RequestPermission('huanxing:user:del')),
        DependsRBAC,
    ],
)
async def delete_huanxing_users(db: CurrentSessionTransaction, obj: DeleteHuanxingUserParam) -> ResponseModel:
    count = await huanxing_user_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
