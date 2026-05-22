"""HASN 知识库凭据 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

import sqlalchemy as sa

from backend.app.hasn.model import HasnRagflowCredential, HasnRagflowInstance
from backend.app.hasn.util.secret_crypto import decrypt_ragflow_secret
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


class KnowledgeCredentialResponse(BaseModel):
    """知识库凭据响应"""

    status: str = Field(..., description="凭据状态: not_provisioned | pending | active | revoked")
    url: str | None = Field(None, description="RAGFlow 服务地址")
    api_key: str | None = Field(None, description="API Key（已解密）")
    instance_id: int | None = Field(None, description="实例 ID")
    ragflow_user_id: str | None = Field(None, description="RAGFlow 用户 ID")


@router.get(
    '/knowledge/credentials',
    summary='获取当前用户的知识库凭据',
    description='获取当前用户的 RAGFlow 凭据，用于 daemon 初始化知识库适配器',
    dependencies=[DependsJwtAuth],
)
async def get_my_knowledge_credentials(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    """
    获取当前用户的知识库凭据

    返回：
    - status: 凭据状态
      - not_provisioned: 未 provision
      - pending: provision 中
      - active: 已激活
      - revoked: 已撤销
    - url: RAGFlow 服务地址
    - api_key: API Key（已解密）
    - instance_id: 实例 ID
    - ragflow_user_id: RAGFlow 用户 ID
    """
    user_id = request.user.id

    # 查询用户的活跃凭据
    stmt = (
        sa.select(HasnRagflowCredential, HasnRagflowInstance)
        .join(
            HasnRagflowInstance,
            HasnRagflowCredential.instance_id == HasnRagflowInstance.id
        )
        .where(
            HasnRagflowCredential.user_id == user_id,
            HasnRagflowCredential.status.in_(['pending', 'active'])
        )
        .order_by(HasnRagflowCredential.update_time.desc())
        .limit(1)
    )

    result = await db.execute(stmt)
    row = result.first()

    if row is None:
        # 未 provision
        return await response_base.success(
            data=KnowledgeCredentialResponse(
                status='not_provisioned',
                url=None,
                api_key=None,
                instance_id=None,
                ragflow_user_id=None,
            )
        )

    credential, instance = row

    # 解密 API Key
    api_key = None
    if credential.status == 'active' and credential.api_key_encrypted:
        api_key = decrypt_ragflow_secret(credential.api_key_encrypted)

    return await response_base.success(
        data=KnowledgeCredentialResponse(
            status=credential.status,
            url=instance.url if credential.status == 'active' else None,
            api_key=api_key,
            instance_id=instance.id,
            ragflow_user_id=credential.ragflow_user_id if credential.status == 'active' else None,
        )
    )
