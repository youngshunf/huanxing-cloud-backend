from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.huanxing.schema.huanxing_document_autosave import (
    CreateHuanxingDocumentAutosaveParam,
    DeleteHuanxingDocumentAutosaveParam,
    GetHuanxingDocumentAutosaveDetail,
    UpdateHuanxingDocumentAutosaveParam,
)
from backend.app.huanxing.service.huanxing_document_autosave_service import huanxing_document_autosave_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取文档自动保存表（每文档每用户仅一条，UPSERT更新）详情', dependencies=[DependsJwtAuth])
async def get_huanxing_document_autosave(
    db: CurrentSession, pk: Annotated[int, Path(description='文档自动保存表（每文档每用户仅一条，UPSERT更新） ID')]
) -> ResponseSchemaModel[GetHuanxingDocumentAutosaveDetail]:
    huanxing_document_autosave = await huanxing_document_autosave_service.get(db=db, pk=pk)
    return response_base.success(data=huanxing_document_autosave)


@router.get(
    '',
    summary='分页获取所有文档自动保存表（每文档每用户仅一条，UPSERT更新）',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_huanxing_document_autosaves_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHuanxingDocumentAutosaveDetail]]:
    page_data = await huanxing_document_autosave_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建文档自动保存表（每文档每用户仅一条，UPSERT更新）',
    dependencies=[
        Depends(RequestPermission('huanxing:document:autosave:add')),
        DependsRBAC,
    ],
)
async def create_huanxing_document_autosave(db: CurrentSessionTransaction, obj: CreateHuanxingDocumentAutosaveParam) -> ResponseModel:
    await huanxing_document_autosave_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新文档自动保存表（每文档每用户仅一条，UPSERT更新）',
    dependencies=[
        Depends(RequestPermission('huanxing:document:autosave:edit')),
        DependsRBAC,
    ],
)
async def update_huanxing_document_autosave(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='文档自动保存表（每文档每用户仅一条，UPSERT更新） ID')], obj: UpdateHuanxingDocumentAutosaveParam
) -> ResponseModel:
    count = await huanxing_document_autosave_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除文档自动保存表（每文档每用户仅一条，UPSERT更新）',
    dependencies=[
        Depends(RequestPermission('huanxing:document:autosave:del')),
        DependsRBAC,
    ],
)
async def delete_huanxing_document_autosaves(db: CurrentSessionTransaction, obj: DeleteHuanxingDocumentAutosaveParam) -> ResponseModel:
    count = await huanxing_document_autosave_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
