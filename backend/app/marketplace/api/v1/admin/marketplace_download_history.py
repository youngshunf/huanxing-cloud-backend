from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.marketplace.schema.marketplace_download_history import (
    CreateMarketplaceDownloadHistoryParam,
    DeleteMarketplaceDownloadHistoryParam,
    GetMarketplaceDownloadHistoryDetail,
    UpdateMarketplaceDownloadHistoryParam,
)
from backend.app.marketplace.service.marketplace_download_history_service import marketplace_download_history_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取技能市场下载历史详情', dependencies=[DependsJwtAuth], name='admin_get_marketplace_download_history')
async def get_marketplace_download_history(
    db: CurrentSession, pk: Annotated[int, Path(description='技能市场下载历史 ID')]
) -> ResponseSchemaModel[GetMarketplaceDownloadHistoryDetail]:
    marketplace_download_history = await marketplace_download_history_service.get(db=db, pk=pk)
    return response_base.success(data=marketplace_download_history)


@router.get(
    '',
    summary='分页获取所有技能市场下载历史',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_marketplace_download_history_paginated',
)
async def get_marketplace_download_history_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetMarketplaceDownloadHistoryDetail]]:
    page_data = await marketplace_download_history_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建技能市场下载历史',
    dependencies=[
        Depends(RequestPermission('marketplace:download:history:add')),
        DependsRBAC,
    ],
    name='admin_create_marketplace_download_history',
)
async def create_marketplace_download_history(db: CurrentSessionTransaction, obj: CreateMarketplaceDownloadHistoryParam) -> ResponseModel:
    await marketplace_download_history_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新技能市场下载历史',
    dependencies=[
        Depends(RequestPermission('marketplace:download:history:edit')),
        DependsRBAC,
    ],
    name='admin_update_marketplace_download_history',
)
async def update_marketplace_download_history(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='技能市场下载历史 ID')], obj: UpdateMarketplaceDownloadHistoryParam
) -> ResponseModel:
    count = await marketplace_download_history_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除技能市场下载历史',
    dependencies=[
        Depends(RequestPermission('marketplace:download:history:del')),
        DependsRBAC,
    ],
    name='admin_delete_marketplace_download_history',
)
async def delete_marketplace_download_history(db: CurrentSessionTransaction, obj: DeleteMarketplaceDownloadHistoryParam) -> ResponseModel:
    count = await marketplace_download_history_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
