"""模板版本 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.marketplace.schema.marketplace_template_version import GetMarketplaceTemplateVersionDetail
from backend.app.marketplace.service.marketplace_template_version_service import marketplace_template_version_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取模板版本列表',
    dependencies=[DependsPagination],
    name='open_get_marketplace_template_version',
)
async def get_marketplace_template_version(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetMarketplaceTemplateVersionDetail]]:
    page_data = await marketplace_template_version_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取模板版本详情',
    name='open_get_marketplace_template_version_detail',
)
async def get_marketplace_template_version_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='模板版本 ID')],
) -> ResponseSchemaModel[GetMarketplaceTemplateVersionDetail]:
    marketplace_template_version = await marketplace_template_version_service.get(db=db, pk=pk)
    return response_base.success(data=marketplace_template_version)
