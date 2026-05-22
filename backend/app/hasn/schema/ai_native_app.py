from datetime import datetime

from pydantic import ConfigDict, Field, model_validator

from backend.common.schema import SchemaBase


class AiNativeAppManifestSchemaBase(SchemaBase):
    app_id: str = Field(description='应用 ID')
    version: str = Field(description='版本号')
    status: str = Field('draft', description='状态')
    workspace_scope: list[str] = Field(default_factory=list, description='workspace 范围')
    collaboration_mode: str = Field('none', description='协作模式')
    manifest_json: dict = Field(default_factory=dict, description='Manifest JSON')
    manifest_hash: str = Field(description='Manifest hash')

    @model_validator(mode='after')
    def _validate_manifest(self):
        if not self.workspace_scope:
            raise ValueError('workspace_scope is required')
        return self


class CreateAiNativeAppManifestParam(AiNativeAppManifestSchemaBase):
    pass


class UpdateAiNativeAppManifestParam(AiNativeAppManifestSchemaBase):
    pass


class DeleteAiNativeAppManifestParam(SchemaBase):
    pks: list[int] = Field(description='Manifest ID 列表')


class GetAiNativeAppManifestDetail(AiNativeAppManifestSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    published_at: datetime | None = None
    created_time: datetime
    updated_time: datetime | None = None
