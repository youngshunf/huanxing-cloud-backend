from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_draft import (
    CreateHxCreatorDraftParam,
    DeleteHxCreatorDraftParam,
    GetHxCreatorDraftDetail,
    UpdateHxCreatorDraftParam,
)
from backend.app.creator.service.hx_creator_draft_service import hx_creator_draft_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取草稿箱详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_draft(
    db: CurrentSession, pk: Annotated[int, Path(description='草稿箱 ID')]
) -> ResponseSchemaModel[GetHxCreatorDraftDetail]:
    hx_creator_draft = await hx_creator_draft_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_draft)


@router.get(
    '',
    summary='分页获取所有草稿箱',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_drafts_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorDraftDetail]]:
    page_data = await hx_creator_draft_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建草稿箱',
    dependencies=[
        Depends(RequestPermission('hx:creator:draft:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_draft(db: CurrentSessionTransaction, obj: CreateHxCreatorDraftParam) -> ResponseModel:
    await hx_creator_draft_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新草稿箱',
    dependencies=[
        Depends(RequestPermission('hx:creator:draft:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_draft(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='草稿箱 ID')], obj: UpdateHxCreatorDraftParam
) -> ResponseModel:
    count = await hx_creator_draft_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除草稿箱',
    dependencies=[
        Depends(RequestPermission('hx:creator:draft:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_drafts(db: CurrentSessionTransaction, obj: DeleteHxCreatorDraftParam) -> ResponseModel:
    count = await hx_creator_draft_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
