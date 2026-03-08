from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_topic import (
    CreateHxCreatorTopicParam,
    DeleteHxCreatorTopicParam,
    GetHxCreatorTopicDetail,
    UpdateHxCreatorTopicParam,
)
from backend.app.creator.service.hx_creator_topic_service import hx_creator_topic_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取选题推荐详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_topic(
    db: CurrentSession, pk: Annotated[int, Path(description='选题推荐 ID')]
) -> ResponseSchemaModel[GetHxCreatorTopicDetail]:
    hx_creator_topic = await hx_creator_topic_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_topic)


@router.get(
    '',
    summary='分页获取所有选题推荐',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_topics_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorTopicDetail]]:
    page_data = await hx_creator_topic_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建选题推荐',
    dependencies=[
        Depends(RequestPermission('hx:creator:topic:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_topic(db: CurrentSessionTransaction, obj: CreateHxCreatorTopicParam) -> ResponseModel:
    await hx_creator_topic_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新选题推荐',
    dependencies=[
        Depends(RequestPermission('hx:creator:topic:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_topic(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='选题推荐 ID')], obj: UpdateHxCreatorTopicParam
) -> ResponseModel:
    count = await hx_creator_topic_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除选题推荐',
    dependencies=[
        Depends(RequestPermission('hx:creator:topic:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_topics(db: CurrentSessionTransaction, obj: DeleteHxCreatorTopicParam) -> ResponseModel:
    count = await hx_creator_topic_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
