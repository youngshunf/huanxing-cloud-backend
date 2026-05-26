"""模板版本 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.marketplace.schema.marketplace_template_version import (
    CreateMarketplaceTemplateVersionParam,
    GetMarketplaceTemplateVersionDetail,
    UpdateMarketplaceTemplateVersionParam,
)
from backend.app.marketplace.service.marketplace_template_version_service import marketplace_template_version_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的模板版本列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_marketplace_template_version',
)
async def get_my_marketplace_template_version(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetMarketplaceTemplateVersionDetail]]:
    page_data = await marketplace_template_version_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建模板版本',
    dependencies=[DependsJwtAuth],
    name='app_create_my_marketplace_template_version',
)
async def create_my_marketplace_template_version(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateMarketplaceTemplateVersionParam,
) -> ResponseModel:
    result = await marketplace_template_version_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取模板版本详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_marketplace_template_version_detail',
)
async def get_my_marketplace_template_version_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='模板版本 ID')],
) -> ResponseSchemaModel[GetMarketplaceTemplateVersionDetail]:
    marketplace_template_version = await marketplace_template_version_service.get(db=db, pk=pk)
    if marketplace_template_version.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该模板版本')
    return response_base.success(data=marketplace_template_version)


@router.put(
    '/{pk}',
    summary='更新模板版本',
    dependencies=[DependsJwtAuth],
    name='app_update_my_marketplace_template_version',
)
async def update_my_marketplace_template_version(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='模板版本 ID')],
    obj: UpdateMarketplaceTemplateVersionParam,
) -> ResponseModel:
    marketplace_template_version = await marketplace_template_version_service.get(db=db, pk=pk)
    if getattr(marketplace_template_version, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该模板版本')
    count = await marketplace_template_version_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除模板版本',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_marketplace_template_version',
)
async def delete_my_marketplace_template_version(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='模板版本 ID')],
) -> ResponseModel:
    user_id = request.user.id
    marketplace_template_version = await marketplace_template_version_service.get(db=db, pk=pk)
    if marketplace_template_version.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该模板版本')
    from backend.app.marketplace.schema.marketplace_template_version import DeleteMarketplaceTemplateVersionParam
    count = await marketplace_template_version_service.delete(db=db, obj=DeleteMarketplaceTemplateVersionParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
