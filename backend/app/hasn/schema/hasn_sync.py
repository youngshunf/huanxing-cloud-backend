"""P0 HASN sync/runtime-report schemas.

These public schemas mirror docs/openapi-hasn-cloud-v1.yaml and add only
server-side optional redacted summary fields needed by the P0 backend service.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from backend.app.hasn.schema.hasn_message_hub import ErrorObject
from backend.common.schema import SchemaBase


RuntimeStatus = Literal['missing', 'offline', 'online', 'degraded', 'failed']
SyncPushStatus = Literal['accepted', 'applied', 'duplicate', 'conflict', 'rejected', 'failed']


class CursorMixin(SchemaBase):
    cursor: str | None = Field(default=None, description='Owner-scoped cursor, e.g. owner:h_xxx:123')


class SyncEventRecord(SchemaBase):
    event_id: str = Field(description='服务端事件 ID')
    event_type: str = Field(description='事件类型')
    revision: int = Field(ge=0, description='Owner 维度单调递增 revision')
    created_at: datetime = Field(description='事件创建时间')
    payload: dict[str, Any] = Field(default_factory=dict, description='脱敏事件载荷')


class SyncPullRequest(CursorMixin):
    owner_id: str = Field(description='Owner HASN ID')
    limit: int = Field(default=100, ge=1, le=500, description='最大事件数')


class SyncPullResponse(SchemaBase):
    events: list[SyncEventRecord] = Field(description='同步事件')
    next_cursor: str = Field(description='下一游标')
    has_more: bool = Field(description='是否还有更多')


class ClientEvent(SchemaBase):
    client_event_id: str = Field(description='客户端事件 ID')
    event_type: str = Field(description='事件类型')
    payload: dict[str, Any] = Field(default_factory=dict, description='脱敏上行载荷')
    hasn_id: str | None = Field(default=None, description='事件主体，可空时默认 owner')
    dedupe_key: str | None = Field(default=None, description='业务幂等键')


class SyncPushRequest(SchemaBase):
    owner_id: str = Field(description='Owner HASN ID')
    node_id: str | None = Field(default=None, description='上报 Node ID')
    events: list[ClientEvent] = Field(description='客户端 outbox 事件')


class SyncPushResponse(SchemaBase):
    accepted: int = Field(ge=0, description='已接收事件数')
    rejected: list[ErrorObject] = Field(default_factory=list, description='被拒绝事件')
    next_cursor: str = Field(description='下一游标')


class RuntimeSummary(SchemaBase):
    agent_id: str = Field(description='Agent HASN ID')
    binding_id: str | None = Field(default=None, description='脱敏公共 Binding ID')
    runtime_type: str = Field(description='Runtime 类型')
    status: RuntimeStatus = Field(description='Runtime 摘要状态')
    adapter_registered: bool = Field(default=True, description='RuntimeAdapter 是否已注册')
    handle_available: bool = Field(default=True, description='RuntimeHandle 是否可调度')
    last_seen_at: datetime | None = Field(default=None, description='最后可见时间')
    runtime_revision: int = Field(default=1, ge=0, description='Runtime 摘要修订号')
    summary_json: dict[str, Any] = Field(default_factory=dict, description='脱敏 Runtime 摘要')


class RuntimeReportRequest(SchemaBase):
    owner_id: str = Field(description='Owner HASN ID')
    node_id: str = Field(description='上报 Node ID')
    runtime_summaries: list[RuntimeSummary] = Field(description='Runtime 摘要列表')


class RuntimeReportResponse(SchemaBase):
    accepted: int = Field(ge=0, description='已接收摘要数量')
    rejected: list[ErrorObject] = Field(default_factory=list, description='被拒绝摘要')
    next_cursor: str = Field(description='同步游标')
