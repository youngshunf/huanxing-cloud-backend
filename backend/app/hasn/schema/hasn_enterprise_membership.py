from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class HasnEnterpriseMembershipSchemaBase(SchemaBase):
    enterprise_id: int = Field(description='企业 ID')
    user_id: int = Field(description='用户 ID')
    role: str = Field('member', description='角色')
    status: str = Field('pending', description='状态')
    apply_message: str | None = Field(None, description='申请说明')
    apply_via: str | None = Field(None, description='申请来源')
    invite_code: str | None = Field(None, description='邀请码')
    decided_by: int | None = Field(None, description='审批人')
    decided_at: datetime | None = Field(None, description='审批时间')
    decision_note: str | None = Field(None, description='审批备注')


class CreateHasnEnterpriseMembershipParam(HasnEnterpriseMembershipSchemaBase):
    pass


class UpdateHasnEnterpriseMembershipParam(HasnEnterpriseMembershipSchemaBase):
    pass


class DeleteHasnEnterpriseMembershipParam(SchemaBase):
    pks: list[int] = Field(description='成员关系 ID 列表')


class GetHasnEnterpriseMembershipDetail(HasnEnterpriseMembershipSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
