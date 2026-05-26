from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.marketplace.schema.marketplace_template import (
    CreateMarketplaceTemplateParam,
    DeleteMarketplaceTemplateParam,
    GetMarketplaceTemplateDetail,
    UpdateMarketplaceTemplateParam,
)
from backend.app.marketplace.service.marketplace_template_service import marketplace_template_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取技能市场模板表（Agent模板/技能包/SOP包）详情', dependencies=[DependsJwtAuth], name='admin_get_marketplace_template')
async def get_marketplace_template(
    db: CurrentSession, pk: Annotated[int, Path(description='技能市场模板表（Agent模板/技能包/SOP包） ID')]
) -> ResponseSchemaModel[GetMarketplaceTemplateDetail]:
    marketplace_template = await marketplace_template_service.get(db=db, pk=pk)
    return response_base.success(data=marketplace_template)


@router.get(
    '',
    summary='分页获取所有技能市场模板表（Agent模板/技能包/SOP包）',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_marketplace_template_paginated',
)
async def get_marketplace_template_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetMarketplaceTemplateDetail]]:
    page_data = await marketplace_template_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建技能市场模板表（Agent模板/技能包/SOP包）',
    dependencies=[
        Depends(RequestPermission('marketplace:template:add')),
        DependsRBAC,
    ],
    name='admin_create_marketplace_template',
)
async def create_marketplace_template(db: CurrentSessionTransaction, obj: CreateMarketplaceTemplateParam) -> ResponseModel:
    await marketplace_template_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新技能市场模板表（Agent模板/技能包/SOP包）',
    dependencies=[
        Depends(RequestPermission('marketplace:template:edit')),
        DependsRBAC,
    ],
    name='admin_update_marketplace_template',
)
async def update_marketplace_template(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='技能市场模板表（Agent模板/技能包/SOP包） ID')], obj: UpdateMarketplaceTemplateParam
) -> ResponseModel:
    count = await marketplace_template_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除技能市场模板表（Agent模板/技能包/SOP包）',
    dependencies=[
        Depends(RequestPermission('marketplace:template:del')),
        DependsRBAC,
    ],
    name='admin_delete_marketplace_template',
)
async def delete_marketplace_template(db: CurrentSessionTransaction, obj: DeleteMarketplaceTemplateParam) -> ResponseModel:
    count = await marketplace_template_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
