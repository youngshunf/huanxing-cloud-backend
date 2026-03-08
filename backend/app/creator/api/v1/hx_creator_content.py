from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_content import (
    CreateHxCreatorContentParam,
    DeleteHxCreatorContentParam,
    GetHxCreatorContentDetail,
    UpdateHxCreatorContentParam,
)
from backend.app.creator.service.hx_creator_content_service import hx_creator_content_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取内容创作主详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_content(
    db: CurrentSession, pk: Annotated[int, Path(description='内容创作主 ID')]
) -> ResponseSchemaModel[GetHxCreatorContentDetail]:
    hx_creator_content = await hx_creator_content_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_content)


@router.get(
    '',
    summary='分页获取所有内容创作主',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_contents_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorContentDetail]]:
    page_data = await hx_creator_content_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建内容创作主',
    dependencies=[
        Depends(RequestPermission('hx:creator:content:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_content(db: CurrentSessionTransaction, obj: CreateHxCreatorContentParam) -> ResponseModel:
    await hx_creator_content_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新内容创作主',
    dependencies=[
        Depends(RequestPermission('hx:creator:content:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_content(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='内容创作主 ID')], obj: UpdateHxCreatorContentParam
) -> ResponseModel:
    count = await hx_creator_content_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除内容创作主',
    dependencies=[
        Depends(RequestPermission('hx:creator:content:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_contents(db: CurrentSessionTransaction, obj: DeleteHxCreatorContentParam) -> ResponseModel:
    count = await hx_creator_content_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
