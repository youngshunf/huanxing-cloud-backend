from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.huanxing.schema.huanxing_document import (
    CreateHuanxingDocumentParam,
    UpdateHuanxingDocumentParam,
)
from backend.app.huanxing.schema.huanxing_document_folder import (
    CreateFolderParam,
    MoveFolderParam,
    MoveDocumentParam,
)
from backend.app.huanxing.service.huanxing_document_service import huanxing_document_service
from backend.app.huanxing.service.huanxing_document_folder_service import huanxing_document_folder_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


# ============================================================
# 目录管理
# ============================================================

@router.get(
    '/folders',
    summary='获取目录树',
    dependencies=[DependsJwtAuth],
)
async def agent_get_folder_tree(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    user_id = request.user.id
    tree = await huanxing_document_folder_service.get_tree(db=db, user_id=user_id)
    return response_base.success(data=tree)


@router.post(
    '/folders',
    summary='创建目录',
    dependencies=[DependsJwtAuth],
)
async def agent_create_folder(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateFolderParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await huanxing_document_folder_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.post(
    '/folders/{folder_id}/move',
    summary='移动目录',
    dependencies=[DependsJwtAuth],
)
async def agent_move_folder(
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


@router.delete(
    '/folders/{folder_id}',
    summary='删除目录',
    dependencies=[DependsJwtAuth],
)
async def agent_delete_folder(
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


# ============================================================
# 文档 CRUD
# ============================================================

@router.get(
    '',
    summary='文档列表（支持按目录筛选）',
    dependencies=[DependsJwtAuth],
)
async def agent_list_documents(
    request: Request,
    db: CurrentSession,
    folder_id: Annotated[int | None, Query(description='目录ID（空=根目录）')] = None,
) -> ResponseModel:
    user_id = request.user.id
    contents = await huanxing_document_folder_service.get_folder_contents(
        db=db, folder_id=folder_id, user_id=user_id
    )
    return response_base.success(data=contents)


@router.post(
    '',
    summary='创建文档',
    dependencies=[DependsJwtAuth],
)
async def agent_create_document(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHuanxingDocumentParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await huanxing_document_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取文档详情',
    dependencies=[DependsJwtAuth],
)
async def agent_get_document(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='文档 ID')],
) -> ResponseModel:
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该文档')
    return response_base.success(data={
        'id': document.id,
        'uuid': document.uuid,
        'title': document.title,
        'content': document.content,
        'summary': document.summary,
        'tags': document.tags,
        'word_count': document.word_count,
        'status': document.status,
        'folder_id': document.folder_id,
        'current_version': document.current_version,
        'created_at': document.created_at,
        'updated_at': document.updated_at,
    })


@router.put(
    '/{pk}',
    summary='更新文档',
    dependencies=[DependsJwtAuth],
)
async def agent_update_document(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    obj: UpdateHuanxingDocumentParam,
) -> ResponseModel:
    user_id = request.user.id
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该文档')
    count = await huanxing_document_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除文档',
    dependencies=[DependsJwtAuth],
)
async def agent_delete_document(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
) -> ResponseModel:
    user_id = request.user.id
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该文档')
    from backend.app.huanxing.schema.huanxing_document import DeleteHuanxingDocumentParam
    count = await huanxing_document_service.delete(db=db, obj=DeleteHuanxingDocumentParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.post(
    '/{pk}/move',
    summary='移动文档到指定目录',
    dependencies=[DependsJwtAuth],
)
async def agent_move_document(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    obj: MoveDocumentParam,
) -> ResponseModel:
    user_id = request.user.id
    count = await huanxing_document_folder_service.move_document(
        db=db, document_id=pk, target_folder_id=obj.target_folder_id, user_id=user_id
    )
    if count > 0:
        return response_base.success()
    return response_base.fail()
