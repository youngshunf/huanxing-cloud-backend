"""技能市场下载历史 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.marketplace.schema.marketplace_download_history import GetMarketplaceDownloadHistoryDetail
from backend.app.marketplace.service.marketplace_download_history_service import marketplace_download_history_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取技能市场下载历史列表',
    dependencies=[DependsPagination],
    name='open_get_marketplace_download_history',
)
async def get_marketplace_download_history(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetMarketplaceDownloadHistoryDetail]]:
    page_data = await marketplace_download_history_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取技能市场下载历史详情',
    name='open_get_marketplace_download_history_detail',
)
async def get_marketplace_download_history_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='技能市场下载历史 ID')],
) -> ResponseSchemaModel[GetMarketplaceDownloadHistoryDetail]:
    marketplace_download_history = await marketplace_download_history_service.get(db=db, pk=pk)
    return response_base.success(data=marketplace_download_history)
