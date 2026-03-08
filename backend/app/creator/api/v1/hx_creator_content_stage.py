from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_content_stage import (
    CreateHxCreatorContentStageParam,
    DeleteHxCreatorContentStageParam,
    GetHxCreatorContentStageDetail,
    UpdateHxCreatorContentStageParam,
)
from backend.app.creator.service.hx_creator_content_stage_service import hx_creator_content_stage_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取内容阶段产出详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_content_stage(
    db: CurrentSession, pk: Annotated[int, Path(description='内容阶段产出 ID')]
) -> ResponseSchemaModel[GetHxCreatorContentStageDetail]:
    hx_creator_content_stage = await hx_creator_content_stage_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_content_stage)


@router.get(
    '',
    summary='分页获取所有内容阶段产出',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_content_stages_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorContentStageDetail]]:
    page_data = await hx_creator_content_stage_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建内容阶段产出',
    dependencies=[
        Depends(RequestPermission('hx:creator:content:stage:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_content_stage(db: CurrentSessionTransaction, obj: CreateHxCreatorContentStageParam) -> ResponseModel:
    await hx_creator_content_stage_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新内容阶段产出',
    dependencies=[
        Depends(RequestPermission('hx:creator:content:stage:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_content_stage(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='内容阶段产出 ID')], obj: UpdateHxCreatorContentStageParam
) -> ResponseModel:
    count = await hx_creator_content_stage_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除内容阶段产出',
    dependencies=[
        Depends(RequestPermission('hx:creator:content:stage:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_content_stages(db: CurrentSessionTransaction, obj: DeleteHxCreatorContentStageParam) -> ResponseModel:
    count = await hx_creator_content_stage_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
