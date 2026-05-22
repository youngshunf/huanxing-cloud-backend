"""HASN 知识库凭据 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.app.hasn.service.workbench_domain_service import workbench_domain_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class KnowledgeCredentialResponse(BaseModel):
    """知识库凭据响应"""

    status: str = Field(..., description="凭据状态: not_provisioned | pending | active | revoked")
    url: str | None = Field(None, description="RAGFlow 服务地址")
    api_key: str | None = Field(None, description="API Key（已解密）")
    instance_id: int | None = Field(None, description="实例 ID")
    ragflow_user_id: str | None = Field(None, description="RAGFlow 用户 ID")


class KnowledgeSearchRequest(BaseModel):
    q: str | None = Field(None, description="搜索关键词")
    limit: int | None = Field(None, description="最大条目数")
    dataset_id: str | None = Field(None, description="数据集 ID")


class KnowledgeUploadRequest(BaseModel):
    title: str
    content_text: str
    metadata: dict[str, object] | None = None


class SaveRagflowInstanceRequest(BaseModel):
    url: str
    admin_api_key: str
    public_pem: str
    default_embd_id: str | None = None
    default_llm_id: str | None = None


@router.get(
    '/users/me/knowledge-credentials',
    summary='获取当前用户的知识库凭据',
    description='获取当前用户的 RAGFlow 凭据，用于 daemon 初始化知识库适配器',
    dependencies=[DependsJwtAuth],
)
@router.get(
    '/knowledge/credentials',
    summary='获取当前用户的知识库凭据',
    description='获取当前用户的 RAGFlow 凭据，用于 daemon 初始化知识库适配器',
    dependencies=[DependsJwtAuth],
)
async def get_knowledge_credentials(request: Request, db: CurrentSession) -> ResponseModel:
    data = await workbench_domain_service.get_current_knowledge_credentials(db, user_id=request.user.id)
    return response_base.success(data=data)


get_my_knowledge_credentials = get_knowledge_credentials


@router.post(
    '/users/me/knowledge-credentials/refresh',
    summary='刷新当前用户的知识库凭据',
    description='刷新当前用户的 RAGFlow 凭据，用于 daemon 在工作空间切换后重建适配器状态',
    dependencies=[DependsJwtAuth],
)
@router.post(
    '/knowledge/credentials/refresh',
    summary='刷新当前用户的知识库凭据',
    description='刷新当前用户的 RAGFlow 凭据，用于 daemon 在工作空间切换后重建适配器状态',
    dependencies=[DependsJwtAuth],
)
async def refresh_knowledge_credentials(request: Request, db: CurrentSessionTransaction) -> ResponseModel:
    data = await workbench_domain_service.refresh_current_knowledge_credentials(db, user_id=request.user.id)
    return response_base.success(data=data)


refresh_my_knowledge_credentials = refresh_knowledge_credentials


@router.get(
    '/users/me/knowledge-datasets',
    summary='获取当前用户的知识库数据集',
    dependencies=[DependsJwtAuth],
)
@router.get(
    '/knowledge/datasets',
    summary='获取当前用户的知识库数据集',
    dependencies=[DependsJwtAuth],
)
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


@router.post(
    '/users/me/knowledge-search',
    summary='搜索当前用户的知识库',
    dependencies=[DependsJwtAuth],
)
@router.post(
    '/knowledge/search',
    summary='搜索当前用户的知识库',
    dependencies=[DependsJwtAuth],
)
async def search_knowledge(
    request: Request,
    db: CurrentSession,
    body: KnowledgeSearchRequest,
) -> ResponseModel:
    data = await workbench_domain_service.search_current_knowledge(
        db,
        user_id=request.user.id,
        query=body.q or '',
        limit=body.limit or 50,
        dataset_id=body.dataset_id,
    )
    return response_base.success(data=data)


@router.post(
    '/users/me/knowledge-upload',
    summary='上传知识库文档',
    dependencies=[DependsJwtAuth],
)
@router.post(
    '/knowledge/upload',
    summary='上传知识库文档',
    dependencies=[DependsJwtAuth],
)
async def upload_knowledge_document(
    request: Request,
    db: CurrentSessionTransaction,
    body: KnowledgeUploadRequest,
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
    '/users/me/knowledge-credentials/enterprise/{enterprise_id}',
    summary='获取企业知识库实例',
    dependencies=[DependsJwtAuth],
)
@router.get(
    '/knowledge/enterprise/{enterprise_id}',
    summary='获取企业知识库实例',
    dependencies=[DependsJwtAuth],
)
async def get_enterprise_ragflow_instance(
    request: Request,
    db: CurrentSession,
    enterprise_id: int,
) -> ResponseModel:
    data = await workbench_domain_service.get_enterprise_ragflow_instance(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
    )
    return response_base.success(data=data)


@router.put(
    '/users/me/knowledge-credentials/enterprise/{enterprise_id}',
    summary='保存企业知识库实例',
    dependencies=[DependsJwtAuth],
)
@router.put(
    '/knowledge/enterprise/{enterprise_id}',
    summary='保存企业知识库实例',
    dependencies=[DependsJwtAuth],
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
    '/users/me/knowledge-credentials/enterprise/{enterprise_id}/test',
    summary='测试企业知识库实例',
    dependencies=[DependsJwtAuth],
)
@router.post(
    '/knowledge/enterprise/{enterprise_id}/test',
    summary='测试企业知识库实例',
    dependencies=[DependsJwtAuth],
)
async def test_enterprise_ragflow_instance(
    request: Request,
    db: CurrentSession,
    enterprise_id: int,
) -> ResponseModel:
    data = await workbench_domain_service.test_enterprise_ragflow_instance(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
    )
    return response_base.success(data=data)


@router.delete(
    '/users/me/knowledge-credentials/enterprise/{enterprise_id}',
    summary='禁用企业知识库实例',
    dependencies=[DependsJwtAuth],
)
@router.delete(
    '/knowledge/enterprise/{enterprise_id}',
    summary='禁用企业知识库实例',
    dependencies=[DependsJwtAuth],
)
async def disable_enterprise_ragflow_instance(
    request: Request,
    db: CurrentSession,
    enterprise_id: int,
) -> ResponseModel:
    data = await workbench_domain_service.disable_enterprise_ragflow_instance(
        db,
        enterprise_id=enterprise_id,
        user_id=request.user.id,
    )
    return response_base.success(data=data)
