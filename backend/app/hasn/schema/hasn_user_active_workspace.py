from datetime import datetime

from pydantic import ConfigDict, Field, model_validator

from backend.common.schema import SchemaBase


class HasnUserActiveWorkspaceSchemaBase(SchemaBase):
    user_id: int = Field(description='用户 ID')
    kind: str = Field('personal', description='工作区类型')
    enterprise_id: int | None = Field(None, description='企业 ID')

    @model_validator(mode='after')
    def validate_workspace(self):
        if self.kind == 'personal' and self.enterprise_id is not None:
            raise ValueError('personal workspace cannot have enterprise_id')
        if self.kind == 'enterprise' and self.enterprise_id is None:
            raise ValueError('enterprise workspace requires enterprise_id')
        return self


class CreateHasnUserActiveWorkspaceParam(HasnUserActiveWorkspaceSchemaBase):
    pass


class UpdateHasnUserActiveWorkspaceParam(HasnUserActiveWorkspaceSchemaBase):
    pass


class DeleteHasnUserActiveWorkspaceParam(SchemaBase):
    pks: list[int] = Field(description='用户 ID 列表')


class GetHasnUserActiveWorkspaceDetail(HasnUserActiveWorkspaceSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    switched_at: datetime
