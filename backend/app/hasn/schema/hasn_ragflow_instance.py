from datetime import datetime

from pydantic import ConfigDict, Field, model_validator

from backend.common.schema import SchemaBase


class HasnRagflowInstanceSchemaBase(SchemaBase):
    scope: str = Field(description='作用域')
    enterprise_id: int | None = Field(None, description='企业 ID')
    url: str = Field(description='实例 URL')
    admin_api_key_encrypted: bytes = Field(description='管理员 API Key 密文')
    public_pem: str = Field(description='RSA 公钥')
    default_embd_id: str | None = Field(None, description='默认 Embedding 模型')
    default_llm_id: str | None = Field(None, description='默认 LLM 模型')
    status: str = Field('pending_config', description='状态')

    @model_validator(mode='after')
    def validate_scope(self):
        if self.scope == 'public' and self.enterprise_id is not None:
            raise ValueError('public instance cannot have enterprise_id')
        if self.scope == 'enterprise' and self.enterprise_id is None:
            raise ValueError('enterprise instance requires enterprise_id')
        return self


class CreateHasnRagflowInstanceParam(HasnRagflowInstanceSchemaBase):
    pass


class UpdateHasnRagflowInstanceParam(HasnRagflowInstanceSchemaBase):
    pass


class DeleteHasnRagflowInstanceParam(SchemaBase):
    pks: list[int] = Field(description='RAGFlow 实例 ID 列表')


class GetHasnRagflowInstanceDetail(HasnRagflowInstanceSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
