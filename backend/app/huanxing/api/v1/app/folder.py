from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.huanxing.schema.huanxing_document_folder import (
    CreateFolderParam,
    UpdateFolderParam,
    MoveFolderParam,
    MoveDocumentParam,
)
from backend.app.huanxing.service.huanxing_document_folder_service import huanxing_document_folder_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


# ============================================================
# 目录 CRUD
# ============================================================

@router.get(
    '',
    summary='获取目录树',
    dependencies=[DependsJwtAuth],
)
async def get_folder_tree(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    user_id = request.user.id
    tree = await huanxing_document_folder_service.get_tree(db=db, user_id=user_id)
    return response_base.success(data=tree)


@router.post(
    '',
    summary='创建目录',
    dependencies=[DependsJwtAuth],
)
async def create_folder(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateFolderParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await huanxing_document_folder_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{folder_id}',
    summary='获取目录内容（子目录+文档列表）',
    dependencies=[DependsJwtAuth],
)
async def get_folder_contents(
    request: Request,
    db: CurrentSession,
    folder_id: Annotated[int, Path(description='目录ID')],
) -> ResponseModel:
    user_id = request.user.id
    contents = await huanxing_document_folder_service.get_folder_contents(
        db=db, folder_id=folder_id, user_id=user_id
    )
    return response_base.success(data=contents)


@router.put(
    '/{folder_id}',
    summary='更新目录',
    dependencies=[DependsJwtAuth],
)
async def update_folder(
    request: Request,
    db: CurrentSessionTransaction,
    folder_id: Annotated[int, Path(description='目录ID')],
    obj: UpdateFolderParam,
) -> ResponseModel:
    user_id = request.user.id
    count = await huanxing_document_folder_service.update(db=db, pk=folder_id, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{folder_id}',
    summary='删除目录',
    dependencies=[DependsJwtAuth],
)
async def delete_folder(
    request: Request,
    db: CurrentSessionTransaction,
    folder_id: Annotated[int, Path(description='目录ID')],
    recursive: Annotated[bool, Query(description='是否递归删除')] = False,
) -> ResponseModel:
    user_id = request.user.id
    count = await huanxing_document_folder_service.delete(
        db=db, folder_id=folder_id, user_id=user_id, recursive=recursive
    )
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.post(
    '/{folder_id}/move',
    summary='移动目录',
    dependencies=[DependsJwtAuth],
)
async def move_folder(
    request: Request,
    db: CurrentSessionTransaction,
    folder_id: Annotated[int, Path(description='目录ID')],
    obj: MoveFolderParam,
) -> ResponseModel:
    user_id = request.user.id
    count = await huanxing_document_folder_service.move_folder(
        db=db, folder_id=folder_id, target_parent_id=obj.target_parent_id, user_id=user_id
    )
    return response_base.success(data={'updated': count})
