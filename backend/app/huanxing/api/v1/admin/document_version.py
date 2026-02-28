from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.huanxing.schema.huanxing_document_version import (
    CreateHuanxingDocumentVersionParam,
    DeleteHuanxingDocumentVersionParam,
    GetHuanxingDocumentVersionDetail,
    UpdateHuanxingDocumentVersionParam,
)
from backend.app.huanxing.service.huanxing_document_version_service import huanxing_document_version_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取文档版本历史详情', dependencies=[DependsJwtAuth])
async def get_huanxing_document_version(
    db: CurrentSession, pk: Annotated[int, Path(description='文档版本历史 ID')]
) -> ResponseSchemaModel[GetHuanxingDocumentVersionDetail]:
    huanxing_document_version = await huanxing_document_version_service.get(db=db, pk=pk)
    return response_base.success(data=huanxing_document_version)


@router.get(
    '',
    summary='分页获取所有文档版本历史',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_huanxing_document_versions_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHuanxingDocumentVersionDetail]]:
    page_data = await huanxing_document_version_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建文档版本历史',
    dependencies=[
        Depends(RequestPermission('huanxing:document:version:add')),
        DependsRBAC,
    ],
)
async def create_huanxing_document_version(db: CurrentSessionTransaction, obj: CreateHuanxingDocumentVersionParam) -> ResponseModel:
    await huanxing_document_version_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新文档版本历史',
    dependencies=[
        Depends(RequestPermission('huanxing:document:version:edit')),
        DependsRBAC,
    ],
)
async def update_huanxing_document_version(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='文档版本历史 ID')], obj: UpdateHuanxingDocumentVersionParam
) -> ResponseModel:
    count = await huanxing_document_version_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除文档版本历史',
    dependencies=[
        Depends(RequestPermission('huanxing:document:version:del')),
        DependsRBAC,
    ],
)
async def delete_huanxing_document_versions(db: CurrentSessionTransaction, obj: DeleteHuanxingDocumentVersionParam) -> ResponseModel:
    count = await huanxing_document_version_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
