from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.app.hasn.service.workbench_domain_service import workbench_domain_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction  # noqa: TC001

router = APIRouter()


class SaveRagflowInstanceRequest(BaseModel):
    url: str = Field(description='知识库服务 URL')
    admin_api_key: str = Field(description='管理员 API Key')
    public_pem: str = Field(description='RSA public.pem')
    default_embd_id: str | None = None
    default_llm_id: str | None = None


class KnowledgeSearchRequest(BaseModel):
    q: str | None = None
    limit: int | None = None
    dataset_id: str | None = None


class KnowledgeUploadRequest(BaseModel):
    title: str | None = None
    content_text: str
    metadata: dict[str, Any] | None = None


@router.get('/users/me/knowledge-credentials', dependencies=[DependsJwtAuth], summary='当前工作区知识库凭据')
async def get_knowledge_credentials(request: Request, db: CurrentSession) -> ResponseModel:
    data = await workbench_domain_service.get_current_knowledge_credentials(db, user_id=request.user.id)
    return response_base.success(data=data)


@router.post(
    '/users/me/knowledge-credentials/refresh', dependencies=[DependsJwtAuth], summary='刷新当前工作区知识库凭据'
)
async def refresh_knowledge_credentials(request: Request, db: CurrentSession) -> ResponseModel:
    data = await workbench_domain_service.refresh_current_knowledge_credentials(db, user_id=request.user.id)
    return response_base.success(data=data)


@router.get('/knowledge/datasets', dependencies=[DependsJwtAuth], summary='当前工作区知识库列表')
async def list_knowledge_datasets(
    request: Request,
    db: CurrentSession,
    limit: int = 50,
    offset: int = 0,
) -> ResponseModel:
    data = await workbench_domain_service.list_current_knowledge_datasets(
        db,
        user_id=request.user.id,
        limit=limit,
        offset=offset,
    )
    return response_base.success(data=data)


@router.post('/knowledge/search', dependencies=[DependsJwtAuth], summary='检索当前工作区知识库')
async def search_knowledge(request: Request, db: CurrentSession, body: KnowledgeSearchRequest) -> ResponseModel:
    data = await workbench_domain_service.search_current_knowledge(
        db,
        user_id=request.user.id,
        query=body.q or '',
        limit=body.limit or 50,
        dataset_id=body.dataset_id,
    )
    return response_base.success(data=data)


@router.post('/knowledge/upload', dependencies=[DependsJwtAuth], summary='上传当前工作区知识库文档')
async def upload_knowledge_document(
    request: Request, db: CurrentSession, body: KnowledgeUploadRequest
) -> ResponseModel:
    data = await workbench_domain_service.upload_current_knowledge_document(
        db,
        user_id=request.user.id,
        title=body.title,
        content_text=body.content_text,
        metadata=body.metadata,
    )
    return response_base.success(data=data)


@router.get(
    '/enterprises/{enterprise_id}/ragflow-instance', dependencies=[DependsJwtAuth], summary='企业知识库服务配置'
)
async def get_enterprise_ragflow_instance(request: Request, db: CurrentSession, enterprise_id: int) -> ResponseModel:
    data = await workbench_domain_service.get_enterprise_ragflow_instance(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
    )
    return response_base.success(data=data)


@router.put(
    '/enterprises/{enterprise_id}/ragflow-instance', dependencies=[DependsJwtAuth], summary='保存企业知识库服务配置'
)
async def save_enterprise_ragflow_instance(
    request: Request,
    db: CurrentSessionTransaction,
    enterprise_id: int,
    body: SaveRagflowInstanceRequest,
) -> ResponseModel:
    data = await workbench_domain_service.save_enterprise_ragflow_instance(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
        url=body.url,
        admin_api_key=body.admin_api_key,
        public_pem=body.public_pem,
        default_embd_id=body.default_embd_id,
        default_llm_id=body.default_llm_id,
    )
    return response_base.success(data=data)


@router.post(
    '/enterprises/{enterprise_id}/ragflow-instance/test', dependencies=[DependsJwtAuth], summary='测试企业知识库服务'
)
async def test_enterprise_ragflow_instance(request: Request, db: CurrentSession, enterprise_id: int) -> ResponseModel:
    data = await workbench_domain_service.test_enterprise_ragflow_instance(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
    )
    return response_base.success(data=data)


@router.delete(
    '/enterprises/{enterprise_id}/ragflow-instance', dependencies=[DependsJwtAuth], summary='停用企业知识库服务'
)
async def disable_enterprise_ragflow_instance(
    request: Request, db: CurrentSessionTransaction, enterprise_id: int
) -> ResponseModel:
    data = await workbench_domain_service.disable_enterprise_ragflow_instance(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
    )
    return response_base.success(data=data)
