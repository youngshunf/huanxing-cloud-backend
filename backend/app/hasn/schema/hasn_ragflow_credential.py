from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnRagflowCredentialSchemaBase(SchemaBase):
    user_id: int = Field(description='用户 ID')
    instance_id: int = Field(description='实例 ID')
    ragflow_user_id: str = Field(description='RAGFlow 用户 ID')
    ragflow_tenant_id: str = Field(description='RAGFlow Tenant ID')
    api_key_encrypted: bytes = Field(description='API Key 密文')
    status: str = Field('pending', description='状态')
    last_error: str | None = Field(None, description='最后错误')


class CreateHasnRagflowCredentialParam(HasnRagflowCredentialSchemaBase):
    pass


class UpdateHasnRagflowCredentialParam(HasnRagflowCredentialSchemaBase):
    pass


class DeleteHasnRagflowCredentialParam(SchemaBase):
    pks: list[int] = Field(description='RAGFlow 凭据 ID 列表')


class GetHasnRagflowCredentialDetail(HasnRagflowCredentialSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
