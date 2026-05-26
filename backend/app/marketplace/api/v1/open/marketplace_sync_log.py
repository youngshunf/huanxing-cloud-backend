"""技能市场同步日志 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.marketplace.schema.marketplace_sync_log import GetMarketplaceSyncLogDetail
from backend.app.marketplace.service.marketplace_sync_log_service import marketplace_sync_log_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取技能市场同步日志列表',
    dependencies=[DependsPagination],
    name='open_get_marketplace_sync_log',
)
async def get_marketplace_sync_log(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetMarketplaceSyncLogDetail]]:
    page_data = await marketplace_sync_log_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取技能市场同步日志详情',
    name='open_get_marketplace_sync_log_detail',
)
async def get_marketplace_sync_log_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='技能市场同步日志 ID')],
) -> ResponseSchemaModel[GetMarketplaceSyncLogDetail]:
    marketplace_sync_log = await marketplace_sync_log_service.get(db=db, pk=pk)
    return response_base.success(data=marketplace_sync_log)
