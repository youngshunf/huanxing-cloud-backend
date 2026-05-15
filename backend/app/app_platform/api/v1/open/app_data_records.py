"""应用数据记录表（JSONB 存储） - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.app_platform.schema.app_data_records import GetAppDataRecordsDetail
from backend.app.app_platform.service.app_data_records_service import app_data_records_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取应用数据记录表（JSONB 存储）列表',
    dependencies=[DependsPagination],
 name='open_get_app_data_recordss')
async def get_app_data_recordss(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppDataRecordsDetail]]:
    page_data = await app_data_records_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取应用数据记录表（JSONB 存储）详情',
 name='open_get_app_data_records')
async def get_app_data_records(
    db: CurrentSession,
    pk: Annotated[int, Path(description='应用数据记录表（JSONB 存储） ID')],
) -> ResponseSchemaModel[GetAppDataRecordsDetail]:
    app_data_records = await app_data_records_service.get(db=db, pk=pk)
    return response_base.success(data=app_data_records)
