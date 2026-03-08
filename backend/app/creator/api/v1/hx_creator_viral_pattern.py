from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_viral_pattern import (
    CreateHxCreatorViralPatternParam,
    DeleteHxCreatorViralPatternParam,
    GetHxCreatorViralPatternDetail,
    UpdateHxCreatorViralPatternParam,
)
from backend.app.creator.service.hx_creator_viral_pattern_service import hx_creator_viral_pattern_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取爆款模式库详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_viral_pattern(
    db: CurrentSession, pk: Annotated[int, Path(description='爆款模式库 ID')]
) -> ResponseSchemaModel[GetHxCreatorViralPatternDetail]:
    hx_creator_viral_pattern = await hx_creator_viral_pattern_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_viral_pattern)


@router.get(
    '',
    summary='分页获取所有爆款模式库',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_viral_patterns_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorViralPatternDetail]]:
    page_data = await hx_creator_viral_pattern_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建爆款模式库',
    dependencies=[
        Depends(RequestPermission('hx:creator:viral:pattern:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_viral_pattern(db: CurrentSessionTransaction, obj: CreateHxCreatorViralPatternParam) -> ResponseModel:
    await hx_creator_viral_pattern_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新爆款模式库',
    dependencies=[
        Depends(RequestPermission('hx:creator:viral:pattern:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_viral_pattern(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='爆款模式库 ID')], obj: UpdateHxCreatorViralPatternParam
) -> ResponseModel:
    count = await hx_creator_viral_pattern_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除爆款模式库',
    dependencies=[
        Depends(RequestPermission('hx:creator:viral:pattern:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_viral_patterns(db: CurrentSessionTransaction, obj: DeleteHxCreatorViralPatternParam) -> ResponseModel:
    count = await hx_creator_viral_pattern_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
