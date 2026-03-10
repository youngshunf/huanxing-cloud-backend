from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import Response

from backend.app.huanxing.schema.huanxing_document import (
    CreateHuanxingDocumentParam,
    GetHuanxingDocumentDetail,
    UpdateHuanxingDocumentParam,
    AutosaveParam,
)
from backend.app.huanxing.schema.huanxing_document_folder import MoveDocumentParam
from backend.app.huanxing.service.huanxing_document_service import huanxing_document_service
from backend.app.huanxing.service.huanxing_document_folder_service import huanxing_document_folder_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


# ============================================================
# 文档 CRUD（仅当前用户）
# ============================================================

@router.get(
    '',
    summary='我的文档列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_documents(
    request: Request,
    db: CurrentSession,
    folder_id: int | None = None,
    status: str | None = None,
    title: str | None = None,
) -> ResponseSchemaModel[PageData[GetHuanxingDocumentDetail]]:
    user_id = request.user.id
    page_data = await huanxing_document_service.get_list(
        db=db, user_id=user_id, folder_id=folder_id, status=status, title=title
    )
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建文档',
    dependencies=[DependsJwtAuth],
)
async def create_my_document(
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
async def get_my_document(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='文档 ID')],
) -> ResponseSchemaModel[GetHuanxingDocumentDetail]:
    document = await huanxing_document_service.get(db=db, pk=pk)
    # 校验文档归属
    if document.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该文档')
    return response_base.success(data=document)


@router.put(
    '/{pk}',
    summary='更新文档',
    dependencies=[DependsJwtAuth],
)
async def update_my_document(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    obj: UpdateHuanxingDocumentParam,
) -> ResponseModel:
    user_id = request.user.id
    # 先校验归属
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
async def delete_my_document(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
) -> ResponseModel:
    user_id = request.user.id
    # 校验归属
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该文档')
    from backend.app.huanxing.schema.huanxing_document import DeleteHuanxingDocumentParam
    count = await huanxing_document_service.delete(db=db, obj=DeleteHuanxingDocumentParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()


# ============================================================
# 自动保存
# ============================================================

@router.post(
    '/{pk}/autosave',
    summary='自动保存文档草稿',
    dependencies=[DependsJwtAuth],
)
async def autosave_document(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    obj: AutosaveParam,
) -> ResponseModel:
    user_id = request.user.id
    await huanxing_document_service.autosave(db=db, document_id=pk, user_id=user_id, content=obj.content)
    return response_base.success()


@router.get(
    '/{pk}/autosave',
    summary='获取自动保存的草稿',
    dependencies=[DependsJwtAuth],
)
async def get_autosave_document(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='文档 ID')],
) -> ResponseModel:
    user_id = request.user.id
    autosave = await huanxing_document_service.get_autosave(db=db, document_id=pk, user_id=user_id)
    return response_base.success(data=autosave)


# ============================================================
# 版本历史
# ============================================================

@router.get(
    '/{pk}/versions',
    summary='获取文档版本历史列表',
    dependencies=[DependsJwtAuth],
)
async def get_document_versions(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='文档 ID')],
) -> ResponseModel:
    # 校验归属
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该文档')
    versions = await huanxing_document_service.get_versions(db=db, document_id=pk)
    return response_base.success(data=versions)


@router.get(
    '/{pk}/versions/{version_number}',
    summary='获取指定版本详情',
    dependencies=[DependsJwtAuth],
)
async def get_document_version_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='文档 ID')],
    version_number: Annotated[int, Path(description='版本号')],
) -> ResponseModel:
    # 校验归属
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该文档')
    version = await huanxing_document_service.get_version_detail(
        db=db, document_id=pk, version_number=version_number
    )
    if not version:
        raise errors.NotFoundError(msg='版本不存在')
    return response_base.success(data=version)


@router.post(
    '/{pk}/versions/{version_number}/restore',
    summary='恢复到指定版本',
    dependencies=[DependsJwtAuth],
)
async def restore_document_version(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    version_number: Annotated[int, Path(description='版本号')],
) -> ResponseModel:
    user_id = request.user.id
    # 校验归属
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该文档')
    count = await huanxing_document_service.restore_version(
        db=db, document_id=pk, version_number=version_number, user_id=user_id
    )
    if count > 0:
        return response_base.success()
    return response_base.fail()


# ============================================================
# 分享管理
# ============================================================

@router.post(
    '/{pk}/share',
    summary='生成/更新分享链接',
    dependencies=[DependsJwtAuth],
)
async def create_share_link(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
    permission: Annotated[str, Query(description='权限(view/edit)')] = 'view',
    expires_hours: Annotated[int, Query(description='过期时间(小时)')] = 72,
    password: Annotated[str | None, Query(description='密码(可选)')] = None,
) -> ResponseModel:
    # 校验归属
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权操作该文档')
    share_url = await huanxing_document_service.update_share_settings(
        db=db,
        document_id=pk,
        permission=permission,
        expires_hours=expires_hours,
        password=password,
    )
    return response_base.success(data={'share_url': share_url})


@router.delete(
    '/{pk}/share',
    summary='取消分享',
    dependencies=[DependsJwtAuth],
)
async def cancel_share_link(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='文档 ID')],
) -> ResponseModel:
    # 校验归属
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权操作该文档')
    count = await huanxing_document_service.cancel_share(db=db, document_id=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


# ============================================================
# 导出
# ============================================================

@router.get(
    '/{pk}/export',
    summary='导出文档(markdown/pdf/docx)',
    dependencies=[DependsJwtAuth],
)
async def export_document(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='文档 ID')],
    format: Annotated[str, Query(description='导出格式(markdown/pdf/docx)')] = 'markdown',
) -> Response:
    # 校验归属
    document = await huanxing_document_service.get(db=db, pk=pk)
    if document.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权操作该文档')
    content, filename, mime_type = await huanxing_document_service.export_document(
        db=db,
        document_id=pk,
        format=format,
    )
    encoded_filename = quote(filename)
    return Response(
        content=content,
        media_type=mime_type,
        headers={'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


# ============================================================
# 移动文档到目录
# ============================================================

@router.post(
    '/{pk}/move',
    summary='移动文档到指定目录',
    dependencies=[DependsJwtAuth],
)
async def move_document(
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
