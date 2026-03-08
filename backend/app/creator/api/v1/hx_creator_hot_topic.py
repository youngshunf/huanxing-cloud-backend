from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_hot_topic import (
    CreateHxCreatorHotTopicParam,
    DeleteHxCreatorHotTopicParam,
    GetHxCreatorHotTopicDetail,
    UpdateHxCreatorHotTopicParam,
)
from backend.app.creator.service.hx_creator_hot_topic_service import hx_creator_hot_topic_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取热榜快照详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_hot_topic(
    db: CurrentSession, pk: Annotated[int, Path(description='热榜快照 ID')]
) -> ResponseSchemaModel[GetHxCreatorHotTopicDetail]:
    hx_creator_hot_topic = await hx_creator_hot_topic_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_hot_topic)


@router.get(
    '',
    summary='分页获取所有热榜快照',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_hot_topics_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorHotTopicDetail]]:
    page_data = await hx_creator_hot_topic_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建热榜快照',
    dependencies=[
        Depends(RequestPermission('hx:creator:hot:topic:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_hot_topic(db: CurrentSessionTransaction, obj: CreateHxCreatorHotTopicParam) -> ResponseModel:
    await hx_creator_hot_topic_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新热榜快照',
    dependencies=[
        Depends(RequestPermission('hx:creator:hot:topic:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_hot_topic(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='热榜快照 ID')], obj: UpdateHxCreatorHotTopicParam
) -> ResponseModel:
    count = await hx_creator_hot_topic_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除热榜快照',
    dependencies=[
        Depends(RequestPermission('hx:creator:hot:topic:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_hot_topics(db: CurrentSessionTransaction, obj: DeleteHxCreatorHotTopicParam) -> ResponseModel:
    count = await hx_creator_hot_topic_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
