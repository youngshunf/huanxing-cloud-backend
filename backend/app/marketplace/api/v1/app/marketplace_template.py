"""技能市场模板表（Agent模板/技能包/SOP包） - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.marketplace.schema.marketplace_template import (
    CreateMarketplaceTemplateParam,
    GetMarketplaceTemplateDetail,
    UpdateMarketplaceTemplateParam,
)
from backend.app.marketplace.service.marketplace_template_service import marketplace_template_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的技能市场模板表（Agent模板/技能包/SOP包）列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_marketplace_template',
)
async def get_my_marketplace_template(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetMarketplaceTemplateDetail]]:
    page_data = await marketplace_template_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建技能市场模板表（Agent模板/技能包/SOP包）',
    dependencies=[DependsJwtAuth],
    name='app_create_my_marketplace_template',
)
async def create_my_marketplace_template(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateMarketplaceTemplateParam,
) -> ResponseModel:
    result = await marketplace_template_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取技能市场模板表（Agent模板/技能包/SOP包）详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_marketplace_template_detail',
)
async def get_my_marketplace_template_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='技能市场模板表（Agent模板/技能包/SOP包） ID')],
) -> ResponseSchemaModel[GetMarketplaceTemplateDetail]:
    marketplace_template = await marketplace_template_service.get(db=db, pk=pk)
    if marketplace_template.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该技能市场模板表（Agent模板/技能包/SOP包）')
    return response_base.success(data=marketplace_template)


@router.put(
    '/{pk}',
    summary='更新技能市场模板表（Agent模板/技能包/SOP包）',
    dependencies=[DependsJwtAuth],
    name='app_update_my_marketplace_template',
)
async def update_my_marketplace_template(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='技能市场模板表（Agent模板/技能包/SOP包） ID')],
    obj: UpdateMarketplaceTemplateParam,
) -> ResponseModel:
    marketplace_template = await marketplace_template_service.get(db=db, pk=pk)
    if getattr(marketplace_template, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该技能市场模板表（Agent模板/技能包/SOP包）')
    count = await marketplace_template_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除技能市场模板表（Agent模板/技能包/SOP包）',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_marketplace_template',
)
async def delete_my_marketplace_template(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='技能市场模板表（Agent模板/技能包/SOP包） ID')],
) -> ResponseModel:
    user_id = request.user.id
    marketplace_template = await marketplace_template_service.get(db=db, pk=pk)
    if marketplace_template.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该技能市场模板表（Agent模板/技能包/SOP包）')
    from backend.app.marketplace.schema.marketplace_template import DeleteMarketplaceTemplateParam
    count = await marketplace_template_service.delete(db=db, obj=DeleteMarketplaceTemplateParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
