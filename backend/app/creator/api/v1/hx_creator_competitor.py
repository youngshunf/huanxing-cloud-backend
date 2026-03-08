from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_competitor import (
    CreateHxCreatorCompetitorParam,
    DeleteHxCreatorCompetitorParam,
    GetHxCreatorCompetitorDetail,
    UpdateHxCreatorCompetitorParam,
)
from backend.app.creator.service.hx_creator_competitor_service import hx_creator_competitor_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取竞品账号详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_competitor(
    db: CurrentSession, pk: Annotated[int, Path(description='竞品账号 ID')]
) -> ResponseSchemaModel[GetHxCreatorCompetitorDetail]:
    hx_creator_competitor = await hx_creator_competitor_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_competitor)


@router.get(
    '',
    summary='分页获取所有竞品账号',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_competitors_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorCompetitorDetail]]:
    page_data = await hx_creator_competitor_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建竞品账号',
    dependencies=[
        Depends(RequestPermission('hx:creator:competitor:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_competitor(db: CurrentSessionTransaction, obj: CreateHxCreatorCompetitorParam) -> ResponseModel:
    await hx_creator_competitor_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新竞品账号',
    dependencies=[
        Depends(RequestPermission('hx:creator:competitor:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_competitor(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='竞品账号 ID')], obj: UpdateHxCreatorCompetitorParam
) -> ResponseModel:
    count = await hx_creator_competitor_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除竞品账号',
    dependencies=[
        Depends(RequestPermission('hx:creator:competitor:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_competitors(db: CurrentSessionTransaction, obj: DeleteHxCreatorCompetitorParam) -> ResponseModel:
    count = await hx_creator_competitor_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
