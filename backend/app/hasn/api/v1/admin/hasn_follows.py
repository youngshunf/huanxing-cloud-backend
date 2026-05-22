from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.hasn.schema.hasn_follows import (
    CreateHasnFollowsParam,
    DeleteHasnFollowsParam,
    GetHasnFollowsDetail,
    UpdateHasnFollowsParam,
)
from backend.app.hasn.service.hasn_follows_service import hasn_follows_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取社区关注详情', dependencies=[DependsJwtAuth], name='admin_get_hasn_follows')
async def get_hasn_follows(
    db: CurrentSession, pk: Annotated[int, Path(description='社区关注 ID')]
) -> ResponseSchemaModel[GetHasnFollowsDetail]:
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_follows)


@router.get(
    '',
    summary='分页获取所有社区关注',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_hasn_follows_paginated',
)
async def get_hasn_follows_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnFollowsDetail]]:
    page_data = await hasn_follows_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区关注',
    dependencies=[
        Depends(RequestPermission('hasn:follows:add')),
        DependsRBAC,
    ],
    name='admin_create_hasn_follows',
)
async def create_hasn_follows(db: CurrentSessionTransaction, obj: CreateHasnFollowsParam) -> ResponseModel:
    await hasn_follows_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新社区关注',
    dependencies=[
        Depends(RequestPermission('hasn:follows:edit')),
        DependsRBAC,
    ],
    name='admin_update_hasn_follows',
)
async def update_hasn_follows(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='社区关注 ID')], obj: UpdateHasnFollowsParam
) -> ResponseModel:
    count = await hasn_follows_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除社区关注',
    dependencies=[
        Depends(RequestPermission('hasn:follows:del')),
        DependsRBAC,
    ],
    name='admin_delete_hasn_follows',
)
async def delete_hasn_follows(db: CurrentSessionTransaction, obj: DeleteHasnFollowsParam) -> ResponseModel:
    count = await hasn_follows_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
