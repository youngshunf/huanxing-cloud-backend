from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnEnterpriseInviteCodeSchemaBase(SchemaBase):
    enterprise_id: int = Field(description='企业 ID')
    code: str = Field(description='邀请码')
    created_by: int = Field(description='创建人')
    max_uses: int | None = Field(None, description='最大使用次数')
    used_count: int = Field(0, description='已使用次数')
    expires_at: datetime | None = Field(None, description='过期时间')
    auto_approve: bool = Field(False, description='是否自动审批')
    revoked: bool = Field(False, description='是否撤销')


class CreateHasnEnterpriseInviteCodeParam(HasnEnterpriseInviteCodeSchemaBase):
    pass


class UpdateHasnEnterpriseInviteCodeParam(HasnEnterpriseInviteCodeSchemaBase):
    pass


class DeleteHasnEnterpriseInviteCodeParam(SchemaBase):
    pks: list[int] = Field(description='邀请码 ID 列表')


class GetHasnEnterpriseInviteCodeDetail(HasnEnterpriseInviteCodeSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
