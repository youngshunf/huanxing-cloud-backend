from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_events import (
    CreateAppEventsParam,
    DeleteAppEventsParam,
    GetAppEventsDetail,
    UpdateAppEventsParam,
)
from backend.app.app_platform.service.app_events_service import app_events_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App Event 定义详情', dependencies=[DependsJwtAuth], name='admin_get_app_events')
async def get_app_events(
    db: CurrentSession, pk: Annotated[int, Path(description='App Event 定义 ID')]
) -> ResponseSchemaModel[GetAppEventsDetail]:
    app_events = await app_events_service.get(db=db, pk=pk)
    return response_base.success(data=app_events)


@router.get(
    '',
    summary='分页获取所有App Event 定义',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_eventss_paginated')
async def get_app_eventss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppEventsDetail]]:
    page_data = await app_events_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App Event 定义',
    dependencies=[
        Depends(RequestPermission('app:events:add')),
        DependsRBAC,
    ],
)
async def create_app_events(db: CurrentSessionTransaction, obj: CreateAppEventsParam) -> ResponseModel:
    await app_events_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App Event 定义',
    dependencies=[
        Depends(RequestPermission('app:events:edit')),
        DependsRBAC,
    ],
)
async def update_app_events(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App Event 定义 ID')], obj: UpdateAppEventsParam
) -> ResponseModel:
    count = await app_events_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App Event 定义',
    dependencies=[
        Depends(RequestPermission('app:events:del')),
        DependsRBAC,
    ],
)
async def delete_app_eventss(db: CurrentSessionTransaction, obj: DeleteAppEventsParam) -> ResponseModel:
    count = await app_events_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
