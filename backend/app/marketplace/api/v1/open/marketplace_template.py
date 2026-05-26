"""技能市场模板表（Agent模板/技能包/SOP包） - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.marketplace.schema.marketplace_template import GetMarketplaceTemplateDetail
from backend.app.marketplace.service.marketplace_template_service import marketplace_template_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取技能市场模板表（Agent模板/技能包/SOP包）列表',
    dependencies=[DependsPagination],
    name='open_get_marketplace_template',
)
async def get_marketplace_template(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetMarketplaceTemplateDetail]]:
    page_data = await marketplace_template_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取技能市场模板表（Agent模板/技能包/SOP包）详情',
    name='open_get_marketplace_template_detail',
)
async def get_marketplace_template_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='技能市场模板表（Agent模板/技能包/SOP包） ID')],
) -> ResponseSchemaModel[GetMarketplaceTemplateDetail]:
    marketplace_template = await marketplace_template_service.get(db=db, pk=pk)
    return response_base.success(data=marketplace_template)
