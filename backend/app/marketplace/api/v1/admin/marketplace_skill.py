from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.marketplace.schema.marketplace_skill import (
    CreateMarketplaceSkillParam,
    DeleteMarketplaceSkillParam,
    GetMarketplaceSkillDetail,
    UpdateMarketplaceSkillParam,
)
from backend.app.marketplace.service.marketplace_skill_service import marketplace_skill_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取技能市场技能详情', dependencies=[DependsJwtAuth], name='admin_get_marketplace_skill')
async def get_marketplace_skill(
    db: CurrentSession, pk: Annotated[int, Path(description='技能市场技能 ID')]
) -> ResponseSchemaModel[GetMarketplaceSkillDetail]:
    marketplace_skill = await marketplace_skill_service.get(db=db, pk=pk)
    return response_base.success(data=marketplace_skill)


@router.get(
    '',
    summary='分页获取所有技能市场技能',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
    name='admin_get_marketplace_skill_paginated',
)
async def get_marketplace_skill_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetMarketplaceSkillDetail]]:
    page_data = await marketplace_skill_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建技能市场技能',
    dependencies=[
        Depends(RequestPermission('marketplace:skill:add')),
        DependsRBAC,
    ],
    name='admin_create_marketplace_skill',
)
async def create_marketplace_skill(db: CurrentSessionTransaction, obj: CreateMarketplaceSkillParam) -> ResponseModel:
    await marketplace_skill_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新技能市场技能',
    dependencies=[
        Depends(RequestPermission('marketplace:skill:edit')),
        DependsRBAC,
    ],
    name='admin_update_marketplace_skill',
)
async def update_marketplace_skill(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='技能市场技能 ID')], obj: UpdateMarketplaceSkillParam
) -> ResponseModel:
    count = await marketplace_skill_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除技能市场技能',
    dependencies=[
        Depends(RequestPermission('marketplace:skill:del')),
        DependsRBAC,
    ],
    name='admin_delete_marketplace_skill',
)
async def delete_marketplace_skill(db: CurrentSessionTransaction, obj: DeleteMarketplaceSkillParam) -> ResponseModel:
    count = await marketplace_skill_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
