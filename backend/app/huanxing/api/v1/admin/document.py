from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request

from backend.app.huanxing.schema.huanxing_document import (
    CreateHuanxingDocumentParam,
    DeleteHuanxingDocumentParam,
    GetHuanxingDocumentDetail,
    UpdateHuanxingDocumentParam,
)
from backend.app.huanxing.service.huanxing_document_service import huanxing_document_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='分页获取所有唤星文档',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_huanxing_documents_paginated(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHuanxingDocumentDetail]]:
    page_data = await huanxing_document_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建唤星文档',
    dependencies=[DependsJwtAuth],
)
async def create_huanxing_document(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHuanxingDocumentParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await huanxing_document_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.delete(
    '',
    summary='批量删除唤星文档',
    dependencies=[
        Depends(RequestPermission('huanxing:document:del')),
        DependsRBAC,
    ],
)
async def delete_huanxing_documents(
    db: CurrentSessionTransaction,
    obj: DeleteHuanxingDocumentParam,
) -> ResponseModel:
    count = await huanxing_document_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get('/{pk}', summary='获取唤星文档详情', dependencies=[DependsJwtAuth])
async def get_huanxing_document(
    db: CurrentSession,
    pk: Annotated[int, Path(description='唤星文档 ID')],
) -> ResponseSchemaModel[GetHuanxingDocumentDetail]:
    huanxing_document = await huanxing_document_service.get(db=db, pk=pk)
    return response_base.success(data=huanxing_document)


@router.put(
    '/{pk}',
    summary='更新唤星文档',
    dependencies=[
        Depends(RequestPermission('huanxing:document:edit')),
        DependsRBAC,
    ],
)
async def update_huanxing_document(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='唤星文档 ID')],
    obj: UpdateHuanxingDocumentParam,
) -> ResponseModel:
    user_id = request.user.id
    count = await huanxing_document_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()
