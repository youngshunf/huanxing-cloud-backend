from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette_context.middleware import ContextMiddleware
from starlette_context.plugins import RequestIdPlugin

from backend.app.hasn.api.v1 import ai_native_app as ai_native_api
from backend.app.hasn.api.v1 import message_hub as message_hub_api
from backend.app.hasn.api.v1 import onboarding as onboarding_api
from backend.app.hasn.api.v1.app import knowledge as knowledge_api
from backend.app.hasn.api.v1.app import hasn_skill_bundle as skill_bundle_api
from backend.app.hasn.api.v1.app import hasn_task as task_api
from backend.app.hasn.api.v1.app import hasn_task_run as task_run_api
from backend.app.hasn.api.v1.app import workspace as workspace_api
from backend.app.hasn.api.v1 import sync as sync_api
from backend.app.mcp.routes import mcp_router
from backend.app.hasn.model import HasnAiNativeAppAudit, HasnUserActiveWorkspace
from backend.app.hasn.schema.hasn_message_hub import InboxItem, InboxPullRequest, InboxPullResponse
from backend.app.hasn.schema.hasn_onboarding import SandboxSummary
from backend.app.hasn.service.hasn_message_hub_service import (
    HasnMessageHubService,
    MessageRecord,
    NoopServerSideEffectDispatcher,
    Recipient,
    StoredMessage,
)
from backend.app.hasn.service.hasn_message_hub_service import (
    RuntimeSummary as HubRuntimeSummary,
)
from backend.app.hasn.service.hasn_onboarding_service import (
    DEFAULT_AGENT_DISPLAY_NAME,
    SMS_CODE_PREFIX,
    HasnOnboardingService,
    HasnPhoneAuthService,
)
from backend.app.hasn.service import hasn_onboarding_service as onboarding_service_module
from backend.app.hasn.model import HasnAiNativeAppAudit
from backend.app.hasn.service.ragflow_subscriber import RecordingRAGFlowActions, ragflow_subscriber
from backend.app.hasn.service.hasn_sync_service import HasnSyncService
from backend.app.hasn.service.workspace_notification_subscriber import (
    RecordingWorkspaceNotificationActions,
    workspace_notification_subscriber,
)
from backend.common.exception import errors
from backend.common.exception.exception_handler import register_exception
from backend.common.security.agent_jwt import jwt_encode_agent
from backend.database.db import get_db, get_db_transaction

if TYPE_CHECKING:
    import pytest

P0_AGENT_ID = 'a_p0_default'
P0_OWNER_ID = 'h_p0_owner'
P0_OWNER_USER_ID = 7
P0_AGENT_SESSION_UUID = 'session-p0-agent-jwt'
P0_AGENT_SCOPES = ['message.read', 'knowledge.read']
P0_AGENT_EXPIRE_TIME = datetime(2099, 1, 1, tzinfo=timezone.utc)


def p0_agent_token(agent_name: str = DEFAULT_AGENT_DISPLAY_NAME) -> str:
    return jwt_encode_agent(
        {
            'sub': P0_AGENT_ID,
            'token_type': 'agent',
            'agent_hasn_id': P0_AGENT_ID,
            'agent_name': agent_name,
            'owner_hasn_id': P0_OWNER_ID,
            'owner_user_id': P0_OWNER_USER_ID,
            'scopes': P0_AGENT_SCOPES,
            'session_uuid': P0_AGENT_SESSION_UUID,
            'exp': int(P0_AGENT_EXPIRE_TIME.timestamp()),
        }
    )


async def fake_cloud_current_knowledge_credentials() -> dict[str, Any]:
    return {
        'code': 200,
        'msg': 'ok',
        'data': {
            'workspace': {
                'kind': 'enterprise',
                'user_id': None,
                'enterprise_id': 42,
                'workspace_key': 'enterprise:42',
            },
            'status': 'pending',
            'credential': None,
        },
    }


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, Any] = {}
        self.ttls: dict[str, int] = {}

    async def exists(self, key: str) -> bool:
        return key in self.values

    async def ttl(self, key: str) -> int:
        return self.ttls.get(key, 0)

    async def setex(self, key: str, seconds: int, value: str) -> None:
        self.values[key] = value
        self.ttls[key] = seconds

    async def get(self, key: str) -> Any:
        return self.values.get(key)

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)
        self.ttls.pop(key, None)

    async def delete_prefix(self, prefix: str, exclude: str | list[str] | None = None, batch_size: int = 1000) -> None:
        exclude_set = set(exclude) if isinstance(exclude, list) else {exclude} if isinstance(exclude, str) else set()
        for key in [key for key in self.values if key.startswith(prefix) and key not in exclude_set]:
            await self.delete(key)


class FakeSms:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send_code(self, phone: str, code: str) -> bool:
        self.sent.append((phone, code))
        return True


@dataclass
class FakeUser:
    id: int
    username: str
    nickname: str
    phone: str
    avatar: str | None = None
    bio: str | None = None
    is_multi_login: bool = True
    last_login_time: Any = None


class FakeUserGateway:
    async def get_or_create_phone_user(self, _db: Any, phone: str) -> tuple[FakeUser, bool]:
        return FakeUser(id=7, username=phone, nickname='P0 Dev User', phone=phone), True


class FakeDb:
    def __init__(self) -> None:
        self.workspace_apps: dict[tuple[str, int | None, int | None, str], SimpleNamespace] = {}
        self.active_workspaces: dict[int, SimpleNamespace] = {}
        self.enterprise_memberships: dict[tuple[int, int], SimpleNamespace] = {}
        self.humans_by_user_id: dict[int, SimpleNamespace] = {}
        self.agents_by_hasn_id: dict[str, SimpleNamespace] = {}
        self.audit_rows: list[HasnAiNativeAppAudit] = []

    async def execute(self, stmt: Any) -> Any:
        sql = str(stmt)
        params = getattr(stmt.compile(), 'params', {})
        if 'hasn_agents' in sql:
            if 'hasn_id_1' in params:
                row = self.agents_by_hasn_id.get(params.get('hasn_id_1'))
                return _ScalarResult([row] if row is not None else [])
            rows = [
                agent
                for agent in self.agents_by_hasn_id.values()
                if agent.owner_id == params.get('owner_id_1')
                and (params.get('status_1') is None or agent.status == params.get('status_1'))
            ]
            return _ScalarResult(rows)
        if 'hasn_workspace_app' in sql:
            row = self.workspace_apps.get(
                (
                    params.get('workspace_kind_1'),
                    params.get('user_id_1'),
                    params.get('enterprise_id_1'),
                    params.get('app_id_1'),
                )
            )
            return _ScalarResult([row] if row is not None else [])
        if 'hasn_user_active_workspace' in sql:
            row = self.active_workspaces.get(params.get('user_id_1'))
            return _ScalarResult([row] if row is not None else [])
        if 'hasn_enterprise_membership' in sql:
            row = self.enterprise_memberships.get((params.get('enterprise_id_1'), params.get('user_id_1')))
            return _ScalarResult([row] if row is not None else [])
        if 'hasn_ai_native_app_audit' in sql:
            return _ScalarResult(self._filter_audit_rows(params))
        if 'hasn_ai_native_app_manifest' in sql:
            return _ScalarResult([])
        if 'hasn_humans' in sql:
            row = self.humans_by_user_id.get(params.get('user_id_1'))
            return _ScalarResult([row] if row is not None else [])
        return _ScalarResult([])

    def add(self, row: Any) -> None:
        if row.__class__.__name__ == 'HasnUserActiveWorkspace':
            self.active_workspaces[int(row.user_id)] = row
            return
        if isinstance(row, HasnAiNativeAppAudit):
            if getattr(row, 'id', None) is None:
                row.id = len(self.audit_rows) + 1
            if getattr(row, 'created_at', None) is None:
                row.created_at = datetime(2026, 5, 20, 8, 0, len(self.audit_rows), tzinfo=timezone.utc)
            self.audit_rows.append(row)
            return
        return None

    async def flush(self) -> None:
        return None

    async def refresh(self, row: Any) -> None:
        if isinstance(row, HasnAiNativeAppAudit) and getattr(row, 'id', None) is None:
            row.id = len(self.audit_rows)

    def _filter_audit_rows(self, params: dict[str, Any]) -> list[HasnAiNativeAppAudit]:
        rows = list(self.audit_rows)
        if 'workspace_kind_1' in params:
            rows = [row for row in rows if row.workspace_kind == params['workspace_kind_1']]
        if 'app_id_1' in params:
            rows = [row for row in rows if row.app_id == params['app_id_1']]
        if 'agent_hasn_id_1' in params:
            rows = [row for row in rows if row.agent_hasn_id == params['agent_hasn_id_1']]
        if 'trace_id_1' in params:
            rows = [row for row in rows if row.trace_id == params['trace_id_1']]
        created_at_from = params.get('created_at_1')
        created_at_to = params.get('created_at_2')
        if created_at_from is not None:
            rows = [row for row in rows if row.created_at >= created_at_from]
        if created_at_to is not None:
            rows = [row for row in rows if row.created_at <= created_at_to]
        return rows


@dataclass
class TaskRecord:
    id: int
    owner_id: str
    agent_id: str
    name: str
    description: str | None
    prompt: str
    skill_bundle_ids: list[str]
    skill_ids: list[str]
    workflow_id: int | None
    enabled_toolsets: list[str] | None
    context_from_task_id: int | None
    schedule_type: str
    schedule_config: dict[str, Any]
    schedule_display: str | None
    enabled: bool
    state: str
    next_run_at: Any
    last_run_at: Any
    last_status: str | None
    last_error: str | None
    run_count: int
    repeat_times: int | None
    repeat_completed: int
    create_time: Any
    update_time: Any
    created_time: Any
    updated_time: Any
    created_by: str | None


@dataclass
class SkillBundleRecord:
    id: int
    owner_id: str
    name: str
    display_name: str | None
    description: str | None
    skill_ids: list[str]
    instruction: str | None
    create_time: Any
    update_time: Any
    created_time: Any
    updated_time: Any


@dataclass
class TaskRunRecord:
    id: int
    task_id: int
    agent_id: str
    session_id: str | None
    source_conversation_id: str | None
    source_message_id: str | None
    runtime_node_id: str | None
    status: str
    started_at: Any
    finished_at: Any
    duration_ms: int | None
    prompt_snapshot: str | None
    output: str | None
    error: str | None
    model: str | None
    token_usage: dict[str, Any] | None
    create_time: Any
    created_time: Any
    updated_time: Any


def _fixture_time() -> datetime:
    return datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)


def _page_payload(items: list[Any]) -> dict[str, Any]:
    total = len(items)
    total_pages = 1 if total > 0 else 0
    return {
        'items': items,
        'total': total,
        'page': 1,
        'size': 20,
        'total_pages': total_pages,
        'links': {
            'first': '?page=1&size=20',
            'last': '?page=1&size=20',
            'self': '?page=1&size=20',
            'next': None,
            'prev': None,
        },
    }


@dataclass
class InMemoryTaskStore:
    records: dict[int, TaskRecord] = field(default_factory=dict)
    next_id: int = 1

    async def get_list_by_owner(self, db: Any, owner_id: str) -> dict[str, Any]:
        items = [record for record in self.records.values() if record.owner_id == owner_id]
        items.sort(key=lambda record: record.id, reverse=True)
        return _page_payload(items)

    async def create(self, db: Any, obj: Any) -> TaskRecord:
        payload = obj.model_dump()
        timestamp = _fixture_time()
        create_time = payload.pop('create_time', None) or timestamp
        update_time = payload.pop('update_time', None)
        created_time = payload.pop('created_time', None) or create_time
        updated_time = payload.pop('updated_time', None) or update_time
        record = TaskRecord(
            id=self.next_id,
            **payload,
            create_time=create_time,
            update_time=update_time,
            created_time=created_time,
            updated_time=updated_time,
        )
        self.records[self.next_id] = record
        self.next_id += 1
        return record

    async def get(self, db: Any, pk: int) -> TaskRecord:
        record = self.records.get(pk)
        if record is None:
            raise errors.NotFoundError(msg='任务定义不存在')
        return record

    async def update(self, db: Any, pk: int, obj: Any) -> int:
        record = self.records.get(pk)
        if record is None:
            return 0
        payload = obj.model_dump()
        payload.pop('created_time', None)
        payload.pop('updated_time', None)
        for key, value in payload.items():
            setattr(record, key, value)
        timestamp = _fixture_time()
        record.update_time = timestamp
        record.updated_time = timestamp
        return 1

    async def delete(self, db: Any, obj: Any) -> int:
        deleted = 0
        for pk in obj.pks:
            if pk in self.records:
                del self.records[pk]
                deleted += 1
        return deleted


@dataclass
class InMemorySkillBundleStore:
    records: dict[int, SkillBundleRecord] = field(default_factory=dict)
    next_id: int = 1

    async def get_list_by_owner(self, db: Any, owner_id: str) -> dict[str, Any]:
        items = [record for record in self.records.values() if record.owner_id == owner_id]
        items.sort(key=lambda record: record.id, reverse=True)
        return _page_payload(items)

    async def create(self, db: Any, obj: Any) -> SkillBundleRecord:
        payload = obj.model_dump()
        timestamp = _fixture_time()
        create_time = payload.pop('create_time', None) or timestamp
        update_time = payload.pop('update_time', None)
        created_time = payload.pop('created_time', None) or create_time
        updated_time = payload.pop('updated_time', None) or update_time
        record = SkillBundleRecord(
            id=self.next_id,
            **payload,
            create_time=create_time,
            update_time=update_time,
            created_time=created_time,
            updated_time=updated_time,
        )
        self.records[self.next_id] = record
        self.next_id += 1
        return record

    async def get(self, db: Any, pk: int) -> SkillBundleRecord:
        record = self.records.get(pk)
        if record is None:
            raise errors.NotFoundError(msg='Skill Bundle 定义表（多个 skill 的组合）不存在')
        return record

    async def update(self, db: Any, pk: int, obj: Any) -> int:
        record = self.records.get(pk)
        if record is None:
            return 0
        payload = obj.model_dump()
        payload.pop('created_time', None)
        payload.pop('updated_time', None)
        for key, value in payload.items():
            setattr(record, key, value)
        timestamp = _fixture_time()
        record.update_time = timestamp
        record.updated_time = timestamp
        return 1

    async def delete(self, db: Any, obj: Any) -> int:
        deleted = 0
        for pk in obj.pks:
            if pk in self.records:
                del self.records[pk]
                deleted += 1
        return deleted


@dataclass
class InMemoryTaskRunStore:
    task_store: InMemoryTaskStore
    records: dict[int, TaskRunRecord] = field(default_factory=dict)
    next_id: int = 1

    async def get_list_by_owner(self, db: Any, owner_id: str) -> dict[str, Any]:
        items = [
            record
            for record in self.records.values()
            if (task := self.task_store.records.get(record.task_id)) is not None and task.owner_id == owner_id
        ]
        items.sort(key=lambda record: record.id, reverse=True)
        return _page_payload(items)

    async def create(self, db: Any, obj: Any) -> TaskRunRecord:
        payload = obj.model_dump()
        timestamp = _fixture_time()
        create_time = payload.pop('create_time', None) or timestamp
        created_time = payload.pop('created_time', None) or create_time
        updated_time = payload.pop('updated_time', None)
        record = TaskRunRecord(
            id=self.next_id,
            **payload,
            create_time=create_time,
            created_time=created_time,
            updated_time=updated_time,
        )
        self.records[self.next_id] = record
        self.next_id += 1
        return record

    async def get(self, db: Any, pk: int) -> TaskRunRecord:
        record = self.records.get(pk)
        if record is None:
            raise errors.NotFoundError(msg='任务执行记录不存在')
        return record

    async def update(self, db: Any, pk: int, obj: Any) -> int:
        record = self.records.get(pk)
        if record is None:
            return 0
        payload = obj.model_dump()
        payload.pop('created_time', None)
        payload.pop('updated_time', None)
        for key, value in payload.items():
            setattr(record, key, value)
        timestamp = _fixture_time()
        record.updated_time = timestamp
        return 1

    async def delete(self, db: Any, obj: Any) -> int:
        deleted = 0
        for pk in obj.pks:
            if pk in self.records:
                del self.records[pk]
                deleted += 1
        return deleted


class _ScalarResult:
    def __init__(self, rows: list[Any]) -> None:
        self._rows = list(rows)

    def scalars(self) -> '_ScalarResult':
        return self

    def first(self) -> Any:
        return self._rows[0] if self._rows else None

    def all(self) -> list[Any]:
        return list(self._rows)

    def scalar_one_or_none(self) -> Any:
        return self.first()

    def scalar(self) -> Any:
        return self.first()


class FakeLlmCredentialIssuer:
    async def issue(self, _db: Any, user: FakeUser) -> tuple[str, str, str]:
        return f'sk-p0-{user.id}', 'https://llm.example/v1', 'test-model'


class FakeAgentTokenIssuer:
    def __init__(self, redis: FakeRedis) -> None:
        self.redis = redis

    async def issue(
        self,
        _db: Any,
        *,
        agent_hasn_id: str,
        agent_name: str,
        owner_hasn_id: str,
        owner_user_id: int,
    ) -> SimpleNamespace:
        assert (agent_hasn_id, owner_hasn_id, owner_user_id) == (P0_AGENT_ID, P0_OWNER_ID, P0_OWNER_USER_ID)
        access_token = p0_agent_token(agent_name)
        await self.redis.setex(f'agent_token:{agent_hasn_id}:{P0_AGENT_SESSION_UUID}', 3600, access_token)
        return SimpleNamespace(
            access_token=access_token,
            access_token_expire_time=P0_AGENT_EXPIRE_TIME,
            scopes=P0_AGENT_SCOPES,
        )


class FakeOnboardingGateway:
    def __init__(self) -> None:
        self.node_id: str | None = None
        self.owner_star_id = '100001'

    async def get_user(self, _db: Any, user_id: int) -> FakeUser | None:
        if user_id != 7:
            return None
        return FakeUser(id=7, username='13800138000', nickname='P0 Dev User', phone='13800138000')

    async def ensure_human(self, _db: Any, user: FakeUser) -> tuple[Any, bool]:
        return SimpleNamespace(hasn_id='h_p0_owner', name=user.nickname), True

    async def ensure_node(self, _db: Any, _user_id: int, owner_id: str, request: Any) -> Any:
        assert owner_id == 'h_p0_owner'
        assert 'workspace_path' not in request.node.model_dump_json()
        assert request.node.node_id.startswith('n_')
        self.node_id = request.node.node_id
        return SimpleNamespace(node_id=request.node.node_id)

    async def ensure_owner_binding(self, _db: Any, node_id: str, owner_id: str) -> Any:
        return SimpleNamespace(node_id=node_id, owner_id=owner_id, status='active', sync_revision=1)

    async def ensure_default_agent(self, _db: Any, owner_id: str, node_id: str | None) -> tuple[Any, bool]:
        assert node_id is not None
        assert node_id.startswith('n_')
        if self.node_id is not None:
            assert node_id == self.node_id
        return (
            SimpleNamespace(
                hasn_id='a_p0_default',
                owner_id=owner_id,
                name=DEFAULT_AGENT_DISPLAY_NAME,
                star_id=f'{self.owner_star_id}#assistant',
            ),
            True,
        )

    async def consume_pending_intent(self, _db: Any, pending_intent_id: str, owner_id: str, agent_hasn_id: str) -> bool:
        assert (pending_intent_id, owner_id, agent_hasn_id) == ('pi_p0_real', 'h_p0_owner', 'a_p0_default')
        return True

    async def get_sandbox_summary(self, _db: Any, owner_id: str) -> SandboxSummary | None:
        assert owner_id == 'h_p0_owner'
        return SandboxSummary(sandbox_id='sb_p0_owner', status='active', base_url=None)


@dataclass
class InMemorySyncGateway:
    reports: list[dict[str, Any]] = field(default_factory=list)
    client_events: list[Any] = field(default_factory=list)
    sync_events: list[Any] = field(default_factory=list)
    owner_user_ids: dict[str, int] = field(default_factory=lambda: {'h_p0_owner': 7})
    namespace_revisions: dict[tuple[str, str, str], dict[str, Any]] = field(default_factory=dict)

    async def owns_owner(self, _db: Any, *, owner_id: str, user_id: int) -> bool:
        return self.owner_user_ids.get(owner_id) == user_id

    async def save_runtime_report(self, _db: Any, report: dict[str, Any]) -> None:
        self.reports.append(report)

    async def pull_events(self, _db: Any, *, owner_id: str, after_revision: int, limit: int) -> list[Any]:
        from backend.app.hasn.schema.hasn_sync import SyncEventRecord

        events = [event for event in self.sync_events if event.revision > after_revision]
        if self.reports and not events:
            events.append(SyncEventRecord(
                event_id='se_runtime_reported',
                event_type='runtime.reported',
                revision=max(after_revision + 1, 1),
                created_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
                payload={'owner_id': owner_id, 'reports': len(self.reports), 'limit': limit},
            ))
        return events[:limit]

    async def pull_memory_events(
        self, _db: Any, *, owner_id: str, selections: list[Any], limit: int
    ) -> list[Any]:
        selected = {
            (cursor.sync_scope_kind, cursor.sync_scope_id, cursor.namespace): cursor.last_pulled_revision
            for cursor in selections
        }
        events = []
        for event in self.sync_events:
            key = (
                event.payload.get('sync_scope_kind'),
                event.payload.get('sync_scope_id'),
                event.payload.get('namespace'),
            )
            if key in selected and int(event.payload.get('namespace_revision', 0)) > selected[key]:
                events.append(event)
        return events[:limit]

    async def save_client_event(self, _db: Any, *, owner_id: str, node_id: str, event: Any) -> int | None:
        from backend.app.hasn.schema.hasn_sync import SyncEventRecord

        if not event.event_type.startswith('memory.'):
            self.client_events.append((owner_id, node_id, event))
            return None
        sync_scope_kind = str(event.payload['sync_scope_kind'])
        sync_scope_id = str(event.payload['sync_scope_id'])
        namespace = str(event.payload['namespace'])
        revision_key = (sync_scope_kind, sync_scope_id, namespace)
        previous = self.namespace_revisions.get(revision_key)
        namespace_revision = int(previous['revision']) + 1 if previous else 1
        revision = len(self.sync_events) + 1
        event_id = f'se_memory_{revision}'
        self.sync_events.append(SyncEventRecord(
            event_id=event_id,
            event_type=event.event_type,
            revision=revision,
            created_at=datetime(2026, 5, 1, 0, revision, tzinfo=timezone.utc),
            payload={
                **event.payload,
                'client_event_id': event.client_event_id,
                'node_id': node_id,
                'namespace_revision': namespace_revision,
            },
        ))
        self.namespace_revisions[revision_key] = {'revision': namespace_revision, 'last_event_id': event_id}
        self.client_events.append((owner_id, node_id, event))
        return revision


@dataclass
class InMemoryMessageGateway:
    recipients: dict[str, Recipient]
    runtimes: dict[str, HubRuntimeSummary] = field(default_factory=dict)
    messages: list[StoredMessage] = field(default_factory=list)
    suppressed: list[StoredMessage] = field(default_factory=list)

    async def resolve_recipient(self, _db: Any, target_hasn_id: str) -> Recipient | None:
        return self.recipients.get(target_hasn_id)

    async def latest_runtime_summary(self, _db: Any, *, owner_id: str, agent_hasn_id: str) -> HubRuntimeSummary | None:
        assert owner_id == 'h_p0_owner'
        return self.runtimes.get(agent_hasn_id)

    async def store_inbox_message(self, _db: Any, record: MessageRecord) -> StoredMessage:
        message = StoredMessage(
            message_id=str(len(self.messages) + 1),
            owner_id=record.owner_id,
            hasn_id=record.hasn_id,
            conversation_id=record.conversation_id,
            inbox_kind=record.inbox_kind,
            envelope=dict(record.envelope),
            dispatch_status=record.dispatch_status,
            created_at=datetime(2026, 5, 1, 10, 0, len(self.messages), tzinfo=timezone.utc),
        )
        self.messages.append(message)
        return message

    async def store_suppressed(
        self,
        _db: Any,
        *,
        source_message: StoredMessage,
        reason: str,
        dispatch_status: str,
        runtime_summary: HubRuntimeSummary | None,
    ) -> None:
        assert runtime_summary and runtime_summary.runtime_type == 'hermes'
        source_message.dispatch_status = dispatch_status
        self.suppressed.append(source_message)

    async def mark_dispatch_status(self, _db: Any, *, message_id: str, dispatch_status: str) -> None:
        for message in self.messages:
            if message.message_id == message_id:
                message.dispatch_status = dispatch_status

    async def pull_inbox(self, _db: Any, request: InboxPullRequest, *, limit: int = 100) -> InboxPullResponse:
        items = [
            InboxItem(
                message_id=message.message_id,
                owner_id=message.owner_id,
                hasn_id=message.hasn_id,
                conversation_id=message.conversation_id,
                inbox_kind=message.inbox_kind,
                dispatch_status=message.dispatch_status,
                created_at=message.created_at,
                envelope=message.envelope,
            )
            for message in self.messages[:limit]
        ]
        if request.include_suppressed:
            items.extend(
                InboxItem(
                    message_id=f'suppressed:{message.message_id}',
                    owner_id=message.owner_id,
                    hasn_id=message.hasn_id,
                    conversation_id=message.conversation_id,
                    inbox_kind='suppressed_inbox',
                    dispatch_status=message.dispatch_status,
                    created_at=message.created_at,
                    envelope=message.envelope,
                )
                for message in self.suppressed
            )
        return InboxPullResponse(items=items, next_cursor=f'owner:{request.owner_id}:{len(items)}', has_more=False)


class RecordingFanout:
    def __init__(self) -> None:
        self.pushes: list[tuple[str, dict[str, Any]]] = []

    async def push(self, target_hasn_id: str, payload: dict[str, Any]) -> bool:
        self.pushes.append((target_hasn_id, payload))
        return True


class FailingRuntimeDispatcher:
    async def dispatch(self, target_agent_id: str, payload: dict[str, Any], runtime: HubRuntimeSummary) -> bool:
        assert target_agent_id == 'a_p0_default'
        assert runtime.runtime_type == 'hermes'
        assert payload['method'] == 'hasn.message.received'
        return False


def make_app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    app = FastAPI()
    app.add_middleware(ContextMiddleware, plugins=[RequestIdPlugin(validate=True)])
    register_exception(app)
    app.include_router(onboarding_api.router, prefix='/api/v1/hasn')
    app.include_router(workspace_api.router, prefix='/api/v1/hasn')
    app.include_router(knowledge_api.router, prefix='/api/v1/hasn/app')
    app.include_router(skill_bundle_api.router, prefix='/api/v1/hasn/app/hasn/skill/bundles')
    app.include_router(task_api.router, prefix='/api/v1/hasn/app/hasn/tasks')
    app.include_router(task_run_api.router, prefix='/api/v1/hasn/app/hasn/task/runs')
    app.include_router(sync_api.router, prefix='/api/v1/hasn')
    app.include_router(message_hub_api.router, prefix='/api/v1/hasn')
    app.include_router(ai_native_api.apps_router, prefix='/api/v1/ai-native/apps')
    app.include_router(ai_native_api.runtime_router, prefix='/api/v1/ai-native/runtime')
    app.include_router(ai_native_api.audit_router, prefix='/api/v1/ai-native/audit')
    app.include_router(mcp_router, tags=['MCP'])
    app.add_api_route(
        '/api/v1/hasn/app/users/me/knowledge-credentials',
        fake_cloud_current_knowledge_credentials,
        methods=['GET'],
    )

    fake_db_instance = FakeDb()
    async def fake_db():
        yield fake_db_instance

    class FakeAsyncDbSession:
        async def __aenter__(self) -> FakeDb:
            return fake_db_instance

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
            return False

    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[get_db_transaction] = fake_db
    app.dependency_overrides[sync_api.DependsJwtAuth.dependency] = _fake_jwt_user(7)
    app.dependency_overrides[message_hub_api.DependsJwtAuth.dependency] = _fake_jwt_user(7)
    app.dependency_overrides[onboarding_api.DependsJwtAuth.dependency] = _fake_jwt_user(7)
    monkeypatch.setattr(onboarding_api, 'jwt_decode', lambda _token: SimpleNamespace(id=7))

    async def fake_token_creator(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(access_token='jwt-p0-real-http', session_uuid='session-p0-real-http')

    async def fake_refresh_token_creator(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(refresh_token='refresh-p0-real-http')

    redis = FakeRedis()
    from backend.common.security import agent_jwt as agent_jwt_module
    from backend.app.hasn.service import ai_native_runtime_gateway as ai_native_gateway_module

    monkeypatch.setattr(agent_jwt_module, 'redis_client', redis)
    monkeypatch.setattr(ai_native_gateway_module, 'redis_client', redis)
    monkeypatch.setattr('backend.app.mcp.auth.async_db_session', lambda: FakeAsyncDbSession())
    monkeypatch.setattr('backend.database.db.async_db_session', lambda: FakeAsyncDbSession())
    monkeypatch.setattr('backend.app.mcp.server.HasnCloudMcpServer._log_tool_call', _fake_mcp_log_tool_call)
    monkeypatch.setattr(onboarding_service_module, 'create_refresh_token', fake_refresh_token_creator)
    monkeypatch.setattr(agent_jwt_module, 'get_agent_scopes_cached', _fake_agent_scopes_cached)
    monkeypatch.setattr(
        ai_native_gateway_module.workbench_domain_service,
        'search_current_knowledge',
        _fake_search_current_knowledge,
    )

    task_store = InMemoryTaskStore()
    skill_bundle_store = InMemorySkillBundleStore()
    task_run_store = InMemoryTaskRunStore(task_store=task_store)

    monkeypatch.setattr(task_api.hasn_task_service, 'get_list_by_owner', task_store.get_list_by_owner)
    monkeypatch.setattr(task_api.hasn_task_service, 'create', task_store.create)
    monkeypatch.setattr(task_api.hasn_task_service, 'get', task_store.get)
    monkeypatch.setattr(task_api.hasn_task_service, 'update', task_store.update)
    monkeypatch.setattr(task_api.hasn_task_service, 'delete', task_store.delete)
    monkeypatch.setattr(skill_bundle_api.hasn_skill_bundle_service, 'get_list_by_owner', skill_bundle_store.get_list_by_owner)
    monkeypatch.setattr(skill_bundle_api.hasn_skill_bundle_service, 'create', skill_bundle_store.create)
    monkeypatch.setattr(skill_bundle_api.hasn_skill_bundle_service, 'get', skill_bundle_store.get)
    monkeypatch.setattr(skill_bundle_api.hasn_skill_bundle_service, 'update', skill_bundle_store.update)
    monkeypatch.setattr(skill_bundle_api.hasn_skill_bundle_service, 'delete', skill_bundle_store.delete)
    monkeypatch.setattr(task_run_api.hasn_task_run_service, 'get_list_by_owner', task_run_store.get_list_by_owner)
    monkeypatch.setattr(task_run_api.hasn_task_run_service, 'create', task_run_store.create)
    monkeypatch.setattr(task_run_api.hasn_task_run_service, 'get', task_run_store.get)
    monkeypatch.setattr(task_run_api.hasn_task_run_service, 'update', task_run_store.update)
    monkeypatch.setattr(task_run_api.hasn_task_run_service, 'delete', task_run_store.delete)

    phone_auth = HasnPhoneAuthService(
        redis=redis,
        sms=FakeSms(),
        users=FakeUserGateway(),
        code_generator=lambda: '123456',
        token_creator=fake_token_creator,
        llm_credentials=FakeLlmCredentialIssuer(),
        agent_tokens=FakeAgentTokenIssuer(redis),
    )
    monkeypatch.setattr(onboarding_api, 'hasn_phone_auth_service', phone_auth)
    monkeypatch.setattr(
        onboarding_api,
        'hasn_onboarding_service',
        HasnOnboardingService(gateway=FakeOnboardingGateway(), agent_tokens=FakeAgentTokenIssuer(redis)),
    )
    monkeypatch.setattr(ragflow_subscriber, 'actions', RecordingRAGFlowActions())
    monkeypatch.setattr(workspace_notification_subscriber, 'actions', RecordingWorkspaceNotificationActions())

    sync_gateway = InMemorySyncGateway()
    monkeypatch.setattr(sync_api, 'hasn_sync_service', HasnSyncService(gateway=sync_gateway))

    message_gateway = InMemoryMessageGateway(
        recipients={
            'h_p0_owner': Recipient('h_p0_owner', 'human', 'h_p0_owner'),
            'a_p0_default': Recipient('a_p0_default', 'agent', 'h_p0_owner'),
        },
        runtimes={
            'a_p0_default': HubRuntimeSummary(
                agent_hasn_id='a_p0_default',
                runtime_status='online',
                adapter_registered=True,
                handle_available=True,
                binding_id='bind_p0_default',
                runtime_type='hermes',
                node_id='n_p0_desktop',
                binding_node_id='n_p0_desktop',
                presence='online',
            )
        },
    )
    monkeypatch.setattr(
        message_hub_api,
        'hasn_message_hub_service',
        HasnMessageHubService(
            gateway=message_gateway,
            fanout=RecordingFanout(),
            runtime_dispatcher=FailingRuntimeDispatcher(),
            side_effect_dispatcher=NoopServerSideEffectDispatcher(),
        ),
    )

    redis.values[f'{SMS_CODE_PREFIX}:13800138000'] = '123456'
    fake_db_instance.workspace_apps[('personal', 7, None, 'knowledge')] = SimpleNamespace(
        workspace_kind='personal',
        user_id=7,
        enterprise_id=None,
        app_id='knowledge',
        status='active',
    )
    fake_db_instance.workspace_apps[('enterprise', None, 42, 'knowledge')] = SimpleNamespace(
        workspace_kind='enterprise',
        user_id=None,
        enterprise_id=42,
        app_id='knowledge',
        status='active',
    )
    fake_db_instance.enterprise_memberships[(42, 7)] = SimpleNamespace(
        enterprise_id=42,
        user_id=7,
        role='admin',
        status='approved',
    )
    fake_db_instance.humans_by_user_id[7] = SimpleNamespace(hasn_id='h_p0_owner', user_id=7)
    fake_db_instance.agents_by_hasn_id[P0_AGENT_ID] = SimpleNamespace(
        hasn_id=P0_AGENT_ID,
        owner_id=P0_OWNER_ID,
        name=DEFAULT_AGENT_DISPLAY_NAME,
        display_name=DEFAULT_AGENT_DISPLAY_NAME,
        agent_name=DEFAULT_AGENT_DISPLAY_NAME,
        status='active',
        star_id='100001#assistant',
    )
    fake_db_instance.active_workspaces[7] = HasnUserActiveWorkspace(user_id=7, kind='personal', enterprise_id=None)
    return app


def test_memory_sync_pull_endpoint_filters_by_namespace_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(make_app(monkeypatch))
    auth = {'Authorization': 'Bearer jwt-p0-real-http'}

    owner_push = client.post(
        '/api/v1/hasn/sync/push',
        headers=auth,
        json={
            'owner_id': 'h_p0_owner',
            'node_id': 'n_p0_desktop',
            'events': [
                {
                    'client_event_id': 'ce_memory_owner_event_1',
                    'event_type': 'memory.owner_event.upserted',
                    'hasn_id': 'h_p0_owner',
                    'payload': {
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_p0_owner',
                        'namespace': 'events',
                        'record_id': 'owner_event:h_p0_owner:1',
                        'revision': 1,
                    },
                },
                {
                    'client_event_id': 'ce_memory_owner_event_2',
                    'event_type': 'memory.owner_event.upserted',
                    'hasn_id': 'h_p0_owner',
                    'payload': {
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_p0_owner',
                        'namespace': 'events',
                        'record_id': 'owner_event:h_p0_owner:2',
                        'revision': 2,
                    },
                },
                {
                    'client_event_id': 'ce_memory_owner_fact_1',
                    'event_type': 'memory.owner_fact.upserted',
                    'hasn_id': 'h_p0_owner',
                    'payload': {
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_p0_owner',
                        'namespace': 'facts',
                        'record_id': 'fact:h_p0_owner:1',
                        'revision': 1,
                    },
                },
                {
                    'client_event_id': 'ce_memory_agent_event_1',
                    'event_type': 'memory.agent_self_event.upserted',
                    'hasn_id': 'a_p0_default',
                    'payload': {
                        'sync_scope_kind': 'agent',
                        'sync_scope_id': 'a_p0_default',
                        'namespace': 'agent_events',
                        'record_id': 'agent_event:a_p0_default:1',
                        'revision': 1,
                    },
                },
            ],
        },
    )
    assert owner_push.status_code == 200
    assert owner_push.json()['accepted'] == 4

    pull = client.post(
        '/api/v1/hasn/memory/sync/pull',
        headers=auth,
        json={
            'owner_id': 'h_p0_owner',
            'agent_ids': ['a_p0_default'],
            'namespaces': [
                {'sync_scope_kind': 'owner', 'names': ['events']},
                {'sync_scope_kind': 'agent', 'names': ['agent_events']},
            ],
            'cursors': [
                {
                    'sync_scope_kind': 'owner',
                    'sync_scope_id': 'h_p0_owner',
                    'namespace': 'events',
                    'last_pulled_revision': 1,
                },
                {
                    'sync_scope_kind': 'agent',
                    'sync_scope_id': 'a_p0_default',
                    'namespace': 'agent_events',
                    'last_pulled_revision': 0,
                },
            ],
            'max_events': 10,
        },
    )

    assert pull.status_code == 200, pull.text
    body = pull.json()
    assert [event['event_id'] for event in body['events']] == ['se_memory_2', 'se_memory_4']
    assert [event['payload']['namespace_revision'] for event in body['events']] == [2, 1]
    assert body['next_cursors'] == [
        {
            'sync_scope_kind': 'owner',
            'sync_scope_id': 'h_p0_owner',
            'namespace': 'events',
            'last_pulled_revision': 2,
        },
        {
            'sync_scope_kind': 'agent',
            'sync_scope_id': 'a_p0_default',
            'namespace': 'agent_events',
            'last_pulled_revision': 1,
        },
    ]
    assert body['has_more'] is False


def make_sync_auth_app(monkeypatch: pytest.MonkeyPatch, user_id: int = 7) -> tuple[FastAPI, InMemorySyncGateway]:
    app = FastAPI()
    app.add_middleware(ContextMiddleware, plugins=[RequestIdPlugin(validate=True)])
    register_exception(app)
    app.include_router(sync_api.router, prefix='/api/v1/hasn')

    async def fake_db():
        yield FakeDb()

    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[get_db_transaction] = fake_db
    app.dependency_overrides[sync_api.DependsJwtAuth.dependency] = _fake_jwt_user(user_id)

    sync_gateway = InMemorySyncGateway()
    monkeypatch.setattr(sync_api, 'hasn_sync_service', HasnSyncService(gateway=sync_gateway))
    return app, sync_gateway


def _fake_jwt_user(user_id: int):
    async def fake_jwt(request: Request) -> None:
        request.scope['user'] = SimpleNamespace(id=user_id)

    return fake_jwt


async def _fake_agent_scopes_cached(_agent_hasn_id: str, _db: Any) -> dict[str, Any]:
    return {'scopes': ['message.read', 'knowledge.read'], 'post_needs_review': True}


async def _fake_search_current_knowledge(
    _db: Any,
    *,
    user_id: int,
    query: str,
    limit: int,
    dataset_id: str | None,
) -> dict[str, Any]:
    assert (user_id, limit, dataset_id) == (7, 10, None)
    return {'items': [{'id': 'chunk-1', 'content': query}], 'total': 1}


async def _fake_mcp_log_tool_call(*_args: Any, **_kwargs: Any) -> None:
    return None


def test_p0_real_http_flow_covers_auth_onboarding_sync_runtime_report_message_and_inbox(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = TestClient(make_app(monkeypatch))
    auth = {'Authorization': 'Bearer jwt-p0-real-http'}

    assert client.post('/api/v1/hasn/auth/phone/send_code', json={'phone': '13800138000'}).status_code == 200
    verify = client.post(
        '/api/v1/hasn/auth/phone/verify',
        json={'phone': '13800138000', 'code': '123456', 'pending_intent_id': 'pi_p0_real'},
    )
    assert verify.status_code == 200
    assert verify.json()['access_token'] == 'jwt-p0-real-http'
    assert 'agent_tokens' in verify.json()

    onboarding = client.post(
        '/api/v1/hasn/onboarding/ensure',
        headers=auth,
        json={
            'node': {
                'node_id': 'n_p0_desktop',
                'device_name': 'P0 Desktop',
                'platform': 'macos',
                'client_version': 'p0-real-http',
            },
            'client': {'protocol': 'hasn/0.2', 'supported_extensions': ['sync.pull', 'message_hub']},
            'pending_intent_id': 'pi_p0_real',
        },
    )
    assert onboarding.status_code == 200
    assert onboarding.json()['human']['owner_id'] == 'h_p0_owner'
    assert onboarding.json()['default_agent']['hasn_id'] == 'a_p0_default'
    agent_auth = {'Authorization': f"Bearer {onboarding.json()['default_agent']['access_token']}"}
    agent_mcp_auth = {**agent_auth, 'X-HASN-Agent-ID': 'a_p0_default'}

    mcp_tools = client.post('/mcp/tools/list', headers=agent_mcp_auth, json={})
    assert mcp_tools.status_code == 200, mcp_tools.text
    assert [tool['name'] for tool in mcp_tools.json()['tools']] == ['hasn.tool.search']

    mcp_search = client.post(
        '/mcp/tools/call',
        headers=agent_mcp_auth,
        json={'tool_name': 'hasn.tool.search', 'arguments': {'query': 'sources'}},
    )
    assert mcp_search.status_code == 200, mcp_search.text
    mcp_source_namespaces = {source['namespace'] for source in mcp_search.json()['result']['sources']}
    assert 'hasn.tool' in mcp_source_namespaces

    runtime_report = client.post(
        '/api/v1/hasn/runtime/report',
        headers=auth,
        json={
            'owner_id': 'h_p0_owner',
            'node_id': 'n_p0_desktop',
            'runtime_summaries': [
                {
                    'agent_id': 'a_p0_default',
                    'binding_id': 'bind_p0_default',
                    'runtime_type': 'hermes',
                    'status': 'online',
                    'adapter_registered': True,
                    'handle_available': True,
                    'summary_json': {'capability': 'dispatch'},
                }
            ],
        },
    )
    assert runtime_report.status_code == 200
    assert runtime_report.json()['accepted'] == 1

    sync_push = client.post(
        '/api/v1/hasn/sync/push',
        headers=auth,
        json={
            'owner_id': 'h_p0_owner',
            'node_id': 'n_p0_desktop',
            'events': [{'client_event_id': 'ce_1', 'event_type': 'node.session', 'payload': {'status': 'ready'}}],
        },
    )
    assert sync_push.status_code == 200
    assert sync_push.json()['accepted'] == 1

    memory_push = client.post(
        '/api/v1/hasn/sync/push',
        headers=auth,
        json={
            'owner_id': 'h_p0_owner',
            'node_id': 'n_p0_desktop',
            'events': [
                {
                    'client_event_id': 'ce_memory_owner_event_1',
                    'event_type': 'memory.owner_event.upserted',
                    'hasn_id': 'h_p0_owner',
                    'dedupe_key': 'memory:owner_event:h_p0_owner:1',
                    'payload': {
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_p0_owner',
                        'namespace': 'events',
                        'record_id': 'owner_event:h_p0_owner:1',
                        'revision': 1,
                    },
                }
            ],
        },
    )
    assert memory_push.status_code == 200
    assert memory_push.json()['accepted'] == 1
    assert memory_push.json()['next_cursor'] == 'owner:h_p0_owner:1'

    memory_pull = client.post(
        '/api/v1/hasn/sync/pull',
        headers=auth,
        json={'owner_id': 'h_p0_owner', 'cursor': 'owner:h_p0_owner:0'},
    )
    assert memory_pull.status_code == 200
    assert [event['event_type'] for event in memory_pull.json()['events']] == ['memory.owner_event.upserted']
    assert memory_pull.json()['events'][0]['payload']['namespace'] == 'events'
    assert memory_pull.json()['events'][0]['payload']['namespace_revision'] == 1
    assert memory_pull.json()['next_cursor'] == 'owner:h_p0_owner:1'

    agent_memory_push = client.post(
        '/api/v1/hasn/sync/push',
        headers=auth,
        json={
            'owner_id': 'h_p0_owner',
            'node_id': 'n_p0_desktop',
            'events': [
                {
                    'client_event_id': 'ce_memory_agent_event_1',
                    'event_type': 'memory.agent_self_event.upserted',
                    'hasn_id': 'a_p0_default',
                    'dedupe_key': 'memory:agent_self_event:a_p0_default:1',
                    'payload': {
                        'sync_scope_kind': 'agent',
                        'sync_scope_id': 'a_p0_default',
                        'namespace': 'agent_events',
                        'record_id': 'agent_event:a_p0_default:1',
                        'revision': 1,
                    },
                }
            ],
        },
    )
    assert agent_memory_push.status_code == 200
    assert agent_memory_push.json()['accepted'] == 1
    assert agent_memory_push.json()['next_cursor'] == 'owner:h_p0_owner:2'

    agent_memory_pull = client.post(
        '/api/v1/hasn/sync/pull',
        headers=auth,
        json={'owner_id': 'h_p0_owner', 'cursor': 'owner:h_p0_owner:1'},
    )
    assert agent_memory_pull.status_code == 200
    assert [event['event_type'] for event in agent_memory_pull.json()['events']] == [
        'memory.agent_self_event.upserted'
    ]
    assert agent_memory_pull.json()['events'][0]['payload']['namespace'] == 'agent_events'
    assert agent_memory_pull.json()['events'][0]['payload']['namespace_revision'] == 1
    assert agent_memory_pull.json()['next_cursor'] == 'owner:h_p0_owner:2'

    human_message = client.post(
        '/api/v1/hasn/messages/send',
        headers=auth,
        json={
            'owner_id': 'h_p0_owner',
            'envelope': {
                'conversation_id': '00000000-0000-0000-0000-000000000201',
                'to_id': 'h_p0_owner',
            },
        },
    )
    assert human_message.status_code == 200
    assert human_message.json()['delivery_status'] == 'delivered'
    assert human_message.json()['dispatch_status'] == 'not_required'

    agent_message = client.post(
        '/api/v1/hasn/messages/send',
        headers=auth,
        json={
            'owner_id': 'h_sender',
            'envelope': {
                'conversation_id': '00000000-0000-0000-0000-000000000202',
                'to_id': 'a_p0_default',
            },
        },
    )
    assert agent_message.status_code == 200
    assert agent_message.json()['delivery_status'] == 'delivered'
    assert agent_message.json()['dispatch_status'] == 'dispatch_failed'
    assert agent_message.json()['suppressed_inbox_created'] is True
    assert agent_message.json()['warnings'][0]['name'] == 'ERR_RUNTIME_DISPATCH_FAILED_NON_BLOCKING'

    inbox = client.post(
        '/api/v1/hasn/inbox/pull',
        headers=auth,
        json={'owner_id': 'h_p0_owner', 'include_suppressed': True},
    )
    assert inbox.status_code == 200
    inbox_kinds = [item['inbox_kind'] for item in inbox.json()['items']]
    assert 'human_inbox' in inbox_kinds
    assert 'agent_inbox' in inbox_kinds
    assert 'owner_copy' in inbox_kinds
    assert 'suppressed_inbox' in inbox_kinds

    capabilities = client.post(
        '/api/v1/ai-native/runtime/capabilities',
        headers=agent_auth,
        json={'workspace': None, 'include_disabled': False, 'trace_id': 'trace-cap-personal'},
    )
    assert capabilities.status_code == 200, capabilities.text
    personal_capabilities = capabilities.json()['data']
    assert personal_capabilities['workspace'] == {
        'kind': 'personal',
        'user_id': 7,
        'enterprise_id': None,
        'workspace_key': 'personal:7',
    }
    assert personal_capabilities['tools'][0]['tool_id'] == 'knowledge.search'

    workspace_switch = client.post(
        '/api/v1/hasn/users/me/workspaces/active',
        headers=agent_auth,
        json={'kind': 'enterprise', 'enterprise_id': 42},
    )
    assert workspace_switch.status_code == 200, workspace_switch.text
    assert workspace_switch.json()['data']['active'] == {'kind': 'enterprise', 'enterprise_id': 42}

    enterprise_capabilities = client.post(
        '/api/v1/ai-native/runtime/capabilities',
        headers=agent_auth,
        json={
            'workspace': {'kind': 'enterprise', 'enterprise_id': 42},
            'include_disabled': False,
            'trace_id': 'trace-cap-enterprise',
        },
    )
    assert enterprise_capabilities.status_code == 200, enterprise_capabilities.text
    assert enterprise_capabilities.json()['data']['workspace'] == {
        'kind': 'enterprise',
        'user_id': None,
        'enterprise_id': 42,
        'workspace_key': 'enterprise:42',
    }

    tool_call = client.post(
        '/api/v1/ai-native/runtime/tools/knowledge/knowledge.search/call',
        headers=agent_auth,
        json={
            'workspace': {'kind': 'enterprise', 'enterprise_id': 42},
            'input': {'query': '唤星工作台', 'limit': 10},
            'trace_id': 'trace-tool-enterprise',
        },
    )
    assert tool_call.status_code == 200, tool_call.text
    assert tool_call.json()['data']['decision'] == 'allow'
    assert tool_call.json()['data']['workspace']['workspace_key'] == 'enterprise:42'

    audit = client.get(
        '/api/v1/ai-native/audit',
        params={'app_id': 'knowledge', 'agent_hasn_id': 'a_p0_default', 'trace_id': 'trace-tool-enterprise'},
    )
    assert audit.status_code == 200, audit.text
    assert audit.json()['data']['total'] == 1
    assert audit.json()['data']['items'][0]['tool_id'] == 'knowledge.search'

    invalid_input = client.post(
        '/api/v1/ai-native/runtime/tools/knowledge/knowledge.search/call',
        headers=agent_auth,
        json={
            'workspace': {'kind': 'enterprise', 'enterprise_id': 42},
            'input': {'query': '', 'limit': 0},
            'trace_id': 'trace-tool-invalid-input',
        },
    )
    assert invalid_input.status_code == 200, invalid_input.text
    assert invalid_input.json()['data']['decision'] == 'deny'
    assert invalid_input.json()['data']['error'] == {'code': '15020', 'message': 'input_schema_invalid'}

    invalid_input_audit = client.get(
        '/api/v1/ai-native/audit',
        params={'app_id': 'knowledge', 'agent_hasn_id': 'a_p0_default', 'trace_id': 'trace-tool-invalid-input'},
    )
    assert invalid_input_audit.status_code == 200, invalid_input_audit.text
    assert invalid_input_audit.json()['data']['total'] == 1
    assert invalid_input_audit.json()['data']['items'][0]['error_code'] == '15020'


def test_sync_pull_rejects_owner_not_bound_to_authenticated_user(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _sync_gateway = make_sync_auth_app(monkeypatch, user_id=7)
    client = TestClient(app)

    response = client.post(
        '/api/v1/hasn/sync/pull',
        headers={'Authorization': 'Bearer jwt-p0-owner-mismatch'},
        json={'owner_id': 'h_other_owner', 'cursor': 'owner:h_other_owner:0'},
    )

    assert response.status_code == 403


def test_sync_push_rejects_owner_not_bound_to_authenticated_user(monkeypatch: pytest.MonkeyPatch) -> None:
    app, sync_gateway = make_sync_auth_app(monkeypatch, user_id=7)
    client = TestClient(app)

    response = client.post(
        '/api/v1/hasn/sync/push',
        headers={'Authorization': 'Bearer jwt-p0-owner-mismatch'},
        json={
            'owner_id': 'h_other_owner',
            'node_id': 'n_p0_desktop',
            'events': [
                {
                    'client_event_id': 'ce_unauthorized',
                    'event_type': 'node.session',
                    'payload': {'status': 'ready'},
                }
            ],
        },
    )

    assert response.status_code == 403
    assert sync_gateway.client_events == []


def test_runtime_report_rejects_owner_not_bound_to_authenticated_user(monkeypatch: pytest.MonkeyPatch) -> None:
    app, sync_gateway = make_sync_auth_app(monkeypatch, user_id=7)
    client = TestClient(app)

    response = client.post(
        '/api/v1/hasn/runtime/report',
        headers={'Authorization': 'Bearer jwt-p0-owner-mismatch'},
        json={
            'owner_id': 'h_other_owner',
            'node_id': 'n_p0_desktop',
            'runtime_summaries': [
                {
                    'agent_id': 'a_other_agent',
                    'binding_id': 'bind_other',
                    'runtime_type': 'hermes',
                    'status': 'online',
                    'summary_json': {'capability': 'dispatch'},
                }
            ],
        },
    )

    assert response.status_code == 403
    assert sync_gateway.reports == []


def test_p0_real_http_flow_covers_task_system_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(make_app(monkeypatch))
    auth = {'Authorization': 'Bearer jwt-p0-real-http'}

    bundle_create = client.post(
        '/api/v1/hasn/app/hasn/skill/bundles',
        headers=auth,
        json={
            'owner_id': 'h_other_owner',
            'name': 'backend-dev',
            'display_name': '后端开发',
            'description': 'Backend feature work',
            'skill_ids': ['pytest', 'test-driven-development'],
            'instruction': '先跑测试再汇报。',
            'create_time': None,
            'update_time': None,
        },
    )
    assert bundle_create.status_code == 200, bundle_create.text
    bundle_id = bundle_create.json()['data']['id']
    assert bundle_create.json()['data']['owner_id'] == 'h_p0_owner'

    task_create = client.post(
        '/api/v1/hasn/app/hasn/tasks',
        headers=auth,
        json={
            'owner_id': 'h_other_owner',
            'agent_id': 'a_p0_default',
            'name': '日报任务',
            'description': '生成日报',
            'prompt': '生成日报',
            'skill_bundle_ids': ['backend-dev'],
            'skill_ids': ['pytest'],
            'workflow_id': None,
            'enabled_toolsets': ['terminal'],
            'context_from_task_id': None,
            'schedule_type': 'once',
            'schedule_config': {'run_at': '2026-05-22T09:00:00Z'},
            'schedule_display': '一次性执行',
            'enabled': True,
            'state': 'scheduled',
            'next_run_at': None,
            'last_run_at': None,
            'last_status': None,
            'last_error': None,
            'run_count': 0,
            'repeat_times': None,
            'repeat_completed': 0,
            'create_time': None,
            'update_time': None,
            'created_by': 'tester',
        },
    )
    assert task_create.status_code == 200, task_create.text
    task_id = task_create.json()['data']['id']
    assert task_create.json()['data']['owner_id'] == 'h_p0_owner'
    assert task_create.json()['data']['skill_bundle_ids'] == ['backend-dev']

    tasks = client.get('/api/v1/hasn/app/hasn/tasks', headers=auth)
    assert tasks.status_code == 200, tasks.text
    assert tasks.json()['data']['total'] == 1
    assert tasks.json()['data']['items'][0]['id'] == task_id

    task_detail = client.get(f'/api/v1/hasn/app/hasn/tasks/{task_id}', headers=auth)
    assert task_detail.status_code == 200, task_detail.text
    assert task_detail.json()['data']['name'] == '日报任务'

    task_update = client.put(
        f'/api/v1/hasn/app/hasn/tasks/{task_id}',
        headers=auth,
        json={
            'owner_id': 'h_other_owner',
            'agent_id': 'a_p0_default',
            'name': '日报任务 v2',
            'description': '生成日报并整理',
            'prompt': '生成日报并整理',
            'skill_bundle_ids': ['backend-dev'],
            'skill_ids': ['pytest'],
            'workflow_id': None,
            'enabled_toolsets': ['terminal'],
            'context_from_task_id': None,
            'schedule_type': 'once',
            'schedule_config': {'run_at': '2026-05-22T09:00:00Z'},
            'schedule_display': '一次性执行',
            'enabled': False,
            'state': 'paused',
            'next_run_at': None,
            'last_run_at': None,
            'last_status': None,
            'last_error': None,
            'run_count': 0,
            'repeat_times': None,
            'repeat_completed': 0,
            'create_time': None,
            'update_time': None,
            'created_by': 'tester',
        },
    )
    assert task_update.status_code == 200, task_update.text
    assert task_update.json()['data'] is None

    task_run_create = client.post(
        '/api/v1/hasn/app/hasn/task/runs',
        headers=auth,
        json={
            'task_id': task_id,
            'agent_id': 'a_p0_default',
            'session_id': 'sess_task_1',
            'source_conversation_id': None,
            'source_message_id': None,
            'runtime_node_id': 'n_p0_desktop',
            'status': 'pending',
            'started_at': None,
            'finished_at': None,
            'duration_ms': None,
            'prompt_snapshot': 'Skill bundles: backend-dev\n\n生成日报',
            'output': None,
            'error': None,
            'model': None,
            'token_usage': None,
            'create_time': '2026-05-22T09:00:00Z',
        },
    )
    assert task_run_create.status_code == 200, task_run_create.text
    task_run_id = task_run_create.json()['data']['id']

    task_runs = client.get('/api/v1/hasn/app/hasn/task/runs', headers=auth)
    assert task_runs.status_code == 200, task_runs.text
    assert task_runs.json()['data']['total'] == 1
    assert task_runs.json()['data']['items'][0]['task_id'] == task_id

    task_run_detail = client.get(f'/api/v1/hasn/app/hasn/task/runs/{task_run_id}', headers=auth)
    assert task_run_detail.status_code == 200, task_run_detail.text
    assert task_run_detail.json()['data']['session_id'] == 'sess_task_1'

    bundle_detail = client.get(f'/api/v1/hasn/app/hasn/skill/bundles/{bundle_id}', headers=auth)
    assert bundle_detail.status_code == 200, bundle_detail.text
    assert bundle_detail.json()['data']['skill_ids'] == ['pytest', 'test-driven-development']

    bundle_update = client.put(
        f'/api/v1/hasn/app/hasn/skill/bundles/{bundle_id}',
        headers=auth,
        json={
            'owner_id': 'h_other_owner',
            'name': 'backend-dev',
            'display_name': '后端开发',
            'description': 'Backend feature work updated',
            'skill_ids': ['pytest'],
            'instruction': '先跑测试再汇报。',
            'create_time': None,
            'update_time': None,
        },
    )
    assert bundle_update.status_code == 200, bundle_update.text
    assert bundle_update.json()['data'] is None

    bundle_list = client.get('/api/v1/hasn/app/hasn/skill/bundles', headers=auth)
    assert bundle_list.status_code == 200, bundle_list.text
    assert bundle_list.json()['data']['items'][0]['description'] == 'Backend feature work updated'

    assert client.delete(f'/api/v1/hasn/app/hasn/task/runs/{task_run_id}', headers=auth).status_code == 200
    assert client.delete(f'/api/v1/hasn/app/hasn/tasks/{task_id}', headers=auth).status_code == 200
    assert client.delete(f'/api/v1/hasn/app/hasn/skill/bundles/{bundle_id}', headers=auth).status_code == 200

    task_list_after_delete = client.get('/api/v1/hasn/app/hasn/tasks', headers=auth)
    assert task_list_after_delete.status_code == 200
    assert task_list_after_delete.json()['data']['total'] == 0
