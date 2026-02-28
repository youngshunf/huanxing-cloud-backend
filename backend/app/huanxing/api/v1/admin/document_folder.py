from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.huanxing.schema.huanxing_document_folder import (
    CreateFolderParam,
    UpdateFolderParam,
    DeleteFolderParam,
    GetFolderDetail,
)
from backend.app.huanxing.service.huanxing_document_folder_service import huanxing_document_folder_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='目录列表（管理端）',
    dependencies=[DependsJwtAuth, DependsRBAC, DependsPagination],
)
async def get_folders(
    db: CurrentSession,
    user_id: Annotated[int | None, Query(description='用户ID筛选')] = None,
) -> ResponseSchemaModel[PageData[GetFolderDetail]]:
    page_data = await huanxing_document_folder_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='目录详情',
    dependencies=[DependsJwtAuth, DependsRBAC],
)
async def get_folder(
    db: CurrentSession,
    pk: Annotated[int, Path(description='目录 ID')],
) -> ResponseModel:
    folder = await huanxing_document_folder_service.get(db=db, pk=pk)
    return response_base.success(data=folder)


@router.delete(
    '',
    summary='批量删除目录',
    dependencies=[DependsJwtAuth, DependsRBAC],
)
async def delete_folders(
    db: CurrentSessionTransaction,
    obj: DeleteFolderParam,
) -> ResponseModel:
    from backend.app.huanxing.crud.crud_huanxing_document_folder import huanxing_document_folder_dao
    count = await huanxing_document_folder_dao.delete(db, obj.pks)
    if count > 0:
        return response_base.success()
    return response_base.fail()
