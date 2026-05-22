from datetime import datetime

from pydantic import Field

from backend.common.schema import SchemaBase


class AiNativeRuntimeCapabilitiesRequest(SchemaBase):
    workspace: dict | None = None
    include_disabled: bool = False
    trace_id: str = Field(description='trace id')


class AiNativeToolCallRequest(SchemaBase):
    workspace: dict | None = None
    input: dict = Field(default_factory=dict)
    trace_id: str = Field(description='trace id')


class AiNativeAuditQuery(SchemaBase):
    workspace_kind: str | None = None
    app_id: str | None = None
    agent_hasn_id: str | None = None
    trace_id: str | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None
