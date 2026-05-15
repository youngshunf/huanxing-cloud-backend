"""应用数据记录表（JSONB 存储） - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_data_records import (
    CreateAppDataRecordsParam,
    GetAppDataRecordsDetail,
    UpdateAppDataRecordsParam,
)
from backend.app.app_platform.service.app_data_records_service import app_data_records_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的应用数据记录表（JSONB 存储）列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_data_recordss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppDataRecordsDetail]]:
    page_data = await app_data_records_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用数据记录表（JSONB 存储）',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_data_records(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppDataRecordsParam,
) -> ResponseModel:
    result = await app_data_records_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取应用数据记录表（JSONB 存储）详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_data_records(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')],
) -> ResponseSchemaModel[GetAppDataRecordsDetail]:
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    if app_data_records.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该应用数据记录表（JSONB 存储）')
    return response_base.success(data=app_data_records)


@router.put(
    '/{pk}',
    summary='更新应用数据记录表（JSONB 存储）',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_data_records(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')],
    obj: UpdateAppDataRecordsParam,
) -> ResponseModel:
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    if getattr(app_data_records, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该应用数据记录表（JSONB 存储）')
    count = await app_data_records_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除应用数据记录表（JSONB 存储）',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_data_records(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    if app_data_records.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该应用数据记录表（JSONB 存储）')
    from backend.app.app_platform.schema.app_data_records import DeleteAppDataRecordsParam
    count = await app_data_records_service.delete(db=db, obj=DeleteAppDataRecordsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
