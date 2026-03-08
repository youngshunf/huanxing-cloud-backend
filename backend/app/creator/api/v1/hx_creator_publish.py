from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_publish import (
    CreateHxCreatorPublishParam,
    DeleteHxCreatorPublishParam,
    GetHxCreatorPublishDetail,
    UpdateHxCreatorPublishParam,
)
from backend.app.creator.service.hx_creator_publish_service import hx_creator_publish_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取发布记录详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_publish(
    db: CurrentSession, pk: Annotated[int, Path(description='发布记录 ID')]
) -> ResponseSchemaModel[GetHxCreatorPublishDetail]:
    hx_creator_publish = await hx_creator_publish_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_publish)


@router.get(
    '',
    summary='分页获取所有发布记录',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_publishs_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorPublishDetail]]:
    page_data = await hx_creator_publish_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建发布记录',
    dependencies=[
        Depends(RequestPermission('hx:creator:publish:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_publish(db: CurrentSessionTransaction, obj: CreateHxCreatorPublishParam) -> ResponseModel:
    await hx_creator_publish_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新发布记录',
    dependencies=[
        Depends(RequestPermission('hx:creator:publish:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_publish(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='发布记录 ID')], obj: UpdateHxCreatorPublishParam
) -> ResponseModel:
    count = await hx_creator_publish_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除发布记录',
    dependencies=[
        Depends(RequestPermission('hx:creator:publish:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_publishs(db: CurrentSessionTransaction, obj: DeleteHxCreatorPublishParam) -> ResponseModel:
    count = await hx_creator_publish_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
