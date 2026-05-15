from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_data_records import (
    CreateAppDataRecordsParam,
    DeleteAppDataRecordsParam,
    GetAppDataRecordsDetail,
    UpdateAppDataRecordsParam,
)
from backend.app.app_platform.service.app_data_records_service import app_data_records_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取应用数据记录表（JSONB 存储）详情', dependencies=[DependsJwtAuth], name='admin_get_app_data_records')
async def get_app_data_records(
    db: CurrentSession, pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')]
) -> ResponseSchemaModel[GetAppDataRecordsDetail]:
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    return response_base.success(data=app_data_records)


@router.get(
    '',
    summary='分页获取所有应用数据记录表（JSONB 存储）',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_data_recordss_paginated')
async def get_app_data_recordss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppDataRecordsDetail]]:
    page_data = await app_data_records_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用数据记录表（JSONB 存储）',
    dependencies=[
        Depends(RequestPermission('app:data:records:add')),
        DependsRBAC,
    ],
)
async def create_app_data_records(db: CurrentSessionTransaction, obj: CreateAppDataRecordsParam) -> ResponseModel:
    await app_data_records_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新应用数据记录表（JSONB 存储）',
    dependencies=[
        Depends(RequestPermission('app:data:records:edit')),
        DependsRBAC,
    ],
)
async def update_app_data_records(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')], obj: UpdateAppDataRecordsParam
) -> ResponseModel:
    count = await app_data_records_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除应用数据记录表（JSONB 存储）',
    dependencies=[
        Depends(RequestPermission('app:data:records:del')),
        DependsRBAC,
    ],
)
async def delete_app_data_recordss(db: CurrentSessionTransaction, obj: DeleteAppDataRecordsParam) -> ResponseModel:
    count = await app_data_records_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
