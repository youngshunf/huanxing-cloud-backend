from datetime import datetime

from pydantic import ConfigDict, Field, model_validator

from backend.common.schema import SchemaBase


class HasnWorkspaceAppSchemaBase(SchemaBase):
    workspace_kind: str = Field(description='工作区类型')
    user_id: int | None = Field(None, description='个人空间用户 ID')
    enterprise_id: int | None = Field(None, description='企业空间 ID')
    app_id: str = Field(description='应用 ID')
    status: str = Field('active', description='状态')
    config: dict = Field(default_factory=dict, description='应用配置')
    enabled_by: int | None = Field(None, description='启用人')

    @model_validator(mode='after')
    def validate_workspace(self):
        if self.workspace_kind == 'personal' and (self.user_id is None or self.enterprise_id is not None):
            raise ValueError('personal workspace app requires user_id only')
        if self.workspace_kind == 'enterprise' and (self.enterprise_id is None or self.user_id is not None):
            raise ValueError('enterprise workspace app requires enterprise_id only')
        return self


class CreateHasnWorkspaceAppParam(HasnWorkspaceAppSchemaBase):
    pass


class UpdateHasnWorkspaceAppParam(HasnWorkspaceAppSchemaBase):
    pass


class DeleteHasnWorkspaceAppParam(SchemaBase):
    pks: list[int] = Field(description='工作空间应用 ID 列表')


class GetHasnWorkspaceAppDetail(HasnWorkspaceAppSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enabled_at: datetime
