from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import Response

from backend.app.huanxing.schema.huanxing_document import (
    CreateHuanxingDocumentParam,
    DeleteHuanxingDocumentParam,
    GetHuanxingDocumentDetail,
    UpdateHuanxingDocumentParam,
    AutosaveParam,
)
from backend.app.huanxing.service.huanxing_document_service import huanxing_document_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


# ============================================================
# 固定路径路由放最前面（避免被 /{pk} 匹配）
# ============================================================

@router.get(
    '/share/{share_token}',
    summary='访问分享文档（公开接口，无需登录）',
)
async def get_shared_document(
    db: CurrentSession,
    share_token: Annotated[str, Path(description='分享token')],
    password: Annotated[str | None, Query(description='密码(如需要)')] = None,
) -> ResponseModel:
    document = await huanxing_document_service.get_shared_document(
        db=db,
        share_token=share_token,
        password=password,
    )
    return response_base.success(data=document)


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


# ============================================================
# 带 {pk} 参数的路由
# ============================================================

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
    pk: Annotated[int, Path(description='唤星文档 ID')],
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
    pk: Annotated[int, Path(description='唤星文档 ID')],
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
    db: CurrentSession,
    pk: Annotated[int, Path(description='唤星文档 ID')],
) -> ResponseModel:
    versions = await huanxing_document_service.get_versions(db=db, document_id=pk)
    return response_base.success(data=versions)


@router.get(
    '/{pk}/versions/{version_number}',
    summary='获取指定版本详情',
    dependencies=[DependsJwtAuth],
)
async def get_document_version_detail(
    db: CurrentSession,
    pk: Annotated[int, Path(description='唤星文档 ID')],
    version_number: Annotated[int, Path(description='版本号')],
) -> ResponseModel:
    version = await huanxing_document_service.get_version_detail(
        db=db, document_id=pk, version_number=version_number
    )
    if not version:
        raise errors.NotFoundError(msg='版本不存在')
    return response_base.success(data=version)


@router.post(
    '/{pk}/versions/{version_number}/restore',
    summary='恢复到指定版本',
    dependencies=[
        Depends(RequestPermission('huanxing:document:edit')),
        DependsRBAC,
    ],
)
async def restore_document_version(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='唤星文档 ID')],
    version_number: Annotated[int, Path(description='版本号')],
) -> ResponseModel:
    user_id = request.user.id
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
    dependencies=[
        Depends(RequestPermission('huanxing:document:edit')),
        DependsRBAC,
    ],
)
async def create_share_link(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='唤星文档 ID')],
    permission: Annotated[str, Query(description='权限(view/edit)')] = 'view',
    expires_hours: Annotated[int, Query(description='过期时间(小时)')] = 72,
    password: Annotated[str | None, Query(description='密码(可选)')] = None,
) -> ResponseModel:
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
    dependencies=[
        Depends(RequestPermission('huanxing:document:edit')),
        DependsRBAC,
    ],
)
async def cancel_share_link(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='唤星文档 ID')],
) -> ResponseModel:
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
    db: CurrentSession,
    pk: Annotated[int, Path(description='唤星文档 ID')],
    format: Annotated[str, Query(description='导出格式(markdown/pdf/docx)')] = 'markdown',
) -> Response:
    content, filename, mime_type = await huanxing_document_service.export_document(
        db=db,
        document_id=pk,
        format=format,
    )
    # RFC 5987: 用 filename* 支持中文文件名
    encoded_filename = quote(filename)
    return Response(
        content=content,
        media_type=mime_type,
        headers={'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}"},
    )
