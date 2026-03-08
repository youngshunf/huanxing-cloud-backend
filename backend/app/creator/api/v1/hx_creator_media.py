from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_media import (
    CreateHxCreatorMediaParam,
    DeleteHxCreatorMediaParam,
    GetHxCreatorMediaDetail,
    UpdateHxCreatorMediaParam,
)
from backend.app.creator.service.hx_creator_media_service import hx_creator_media_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取素材库详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_media(
    db: CurrentSession, pk: Annotated[int, Path(description='素材库 ID')]
) -> ResponseSchemaModel[GetHxCreatorMediaDetail]:
    hx_creator_media = await hx_creator_media_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_media)


@router.get(
    '',
    summary='分页获取所有素材库',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_medias_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorMediaDetail]]:
    page_data = await hx_creator_media_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建素材库',
    dependencies=[
        Depends(RequestPermission('hx:creator:media:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_media(db: CurrentSessionTransaction, obj: CreateHxCreatorMediaParam) -> ResponseModel:
    await hx_creator_media_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新素材库',
    dependencies=[
        Depends(RequestPermission('hx:creator:media:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_media(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='素材库 ID')], obj: UpdateHxCreatorMediaParam
) -> ResponseModel:
    count = await hx_creator_media_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除素材库',
    dependencies=[
        Depends(RequestPermission('hx:creator:media:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_medias(db: CurrentSessionTransaction, obj: DeleteHxCreatorMediaParam) -> ResponseModel:
    count = await hx_creator_media_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
