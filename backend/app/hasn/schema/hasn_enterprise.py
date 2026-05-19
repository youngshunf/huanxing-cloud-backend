from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnEnterpriseSchemaBase(SchemaBase):
    name: str = Field(description='企业名称')
    slug: str = Field(description='企业唯一标识')
    logo: str | None = Field(None, description='企业 Logo')
    description: str | None = Field(None, description='企业描述')
    owner_user_id: int = Field(description='企业所有者 sys_user.id')
    join_policy: str = Field('invite_only', description='加入策略')
    status: str = Field('active', description='状态')


class CreateHasnEnterpriseParam(HasnEnterpriseSchemaBase):
    pass


class UpdateHasnEnterpriseParam(HasnEnterpriseSchemaBase):
    pass


class DeleteHasnEnterpriseParam(SchemaBase):
    pks: list[int] = Field(description='企业 ID 列表')


class GetHasnEnterpriseDetail(HasnEnterpriseSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
