from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from backend.app.hasn.schema.hasn_message_hub import MessageHubSendRequest
from backend.app.hasn.service import hasn_onboarding_service as onboarding_mod
from backend.app.hasn.service.hasn_message_hub_service import (
    HasnMessageHubService,
    MessageRecord,
    NoopServerSideEffectDispatcher,
    Recipient,
    RuntimeSummary,
    StoredMessage,
)
from backend.common.exception import errors


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTROL_PLANE_CODEGEN_TABLES = (
    'hasn_agent_runtime_reports',
    'hasn_channel_bindings',
    'hasn_clients',
    'hasn_pending_intents',
    'hasn_suppressed_messages',
    'hasn_sync_events',
    'hasn_sync_inbox_events',
    'hasn_tenant_sandboxes',
)


def test_p0_control_plane_sql_tables_have_codegen_backend_foundation() -> None:
    """P0 tables must have generated backend foundations; CRUD files are codegen-owned."""
    missing: list[str] = []
    for table in CONTROL_PLANE_CODEGEN_TABLES:
        expected = {
            REPO_ROOT / 'backend' / 'app' / 'hasn' / 'model' / f'{table}.py',
            REPO_ROOT / 'backend' / 'app' / 'hasn' / 'schema' / f'{table}.py',
            REPO_ROOT / 'backend' / 'app' / 'hasn' / 'crud' / f'crud_{table}.py',
            REPO_ROOT / 'backend' / 'app' / 'hasn' / 'service' / f'{table}_service.py',
        }
        missing.extend(path.relative_to(REPO_ROOT).as_posix() for path in expected if not path.exists())
    assert missing == []


def test_onboarding_default_agent_uses_assistant_idempotency_key() -> None:
    assert onboarding_mod.DEFAULT_AGENT_NAME == 'assistant'


@dataclass
class GateAwareInMemoryGateway:
    recipients: dict[str, Recipient]
    runtimes: dict[str, RuntimeSummary] = field(default_factory=dict)
    messages: list[StoredMessage] = field(default_factory=list)
    suppressed: list[StoredMessage] = field(default_factory=list)
    dispatch_updates: list[tuple[str, str]] = field(default_factory=list)

    async def resolve_recipient(self, db: Any, target_hasn_id: str) -> Recipient | None:
        return self.recipients.get(target_hasn_id)

    async def latest_runtime_summary(self, db: Any, *, owner_id: str, agent_hasn_id: str) -> RuntimeSummary | None:
        return self.runtimes.get(agent_hasn_id)

    async def store_inbox_message(self, db: Any, record: MessageRecord) -> StoredMessage:
        message = StoredMessage(
            message_id=str(len(self.messages) + 1),
            owner_id=record.owner_id,
            hasn_id=record.hasn_id,
            conversation_id=record.conversation_id,
            inbox_kind=record.inbox_kind,
            envelope=dict(record.envelope),
            dispatch_status=record.dispatch_status,
            created_at=datetime(2026, 5, 1, 8, 0, len(self.messages), tzinfo=timezone.utc),
        )
        self.messages.append(message)
        return message

    async def store_suppressed(
        self,
        db: Any,
        *,
        source_message: StoredMessage,
        reason: str,
        dispatch_status: str,
        runtime_summary: RuntimeSummary | None,
    ) -> None:
        source_message.dispatch_status = dispatch_status
        self.suppressed.append(source_message)

    async def mark_dispatch_status(self, db: Any, *, message_id: str, dispatch_status: str) -> None:
        self.dispatch_updates.append((message_id, dispatch_status))
        for message in self.messages:
            if message.message_id == message_id:
                message.dispatch_status = dispatch_status

    async def pull_inbox(self, db: Any, request: Any, *, limit: int = 100):
        raise NotImplementedError


@dataclass
class RecordingFanout:
    pushes: list[tuple[str, dict[str, Any]]] = field(default_factory=list)

    async def push(self, target_hasn_id: str, payload: dict[str, Any]) -> bool:
        self.pushes.append((target_hasn_id, payload))
        return True


@dataclass
class FailingRuntimeDispatcher:
    async def dispatch(self, target_agent_id: str, payload: dict[str, Any], runtime: RuntimeSummary) -> bool:
        return False


@pytest.mark.asyncio
async def test_runtime_unavailable_agent_delivery_keeps_inbox_reachable() -> None:
    gateway = GateAwareInMemoryGateway(recipients={'a_agent': Recipient('a_agent', 'agent', 'h_owner')})
    fanout = RecordingFanout()
    service = HasnMessageHubService(
        gateway=gateway,
        fanout=fanout,
        runtime_dispatcher=FailingRuntimeDispatcher(),
        side_effect_dispatcher=NoopServerSideEffectDispatcher(),
    )

    response = await service.send(
        None,
        MessageHubSendRequest(
            owner_id='h_sender',
            envelope={'conversation_id': '00000000-0000-0000-0000-000000000101', 'to_id': 'a_agent'},
        ),
    )

    assert response.delivery_status == 'delivered'
    assert response.dispatch_status == 'runtime_unavailable'
    assert response.owner_copy_created is True
    assert response.suppressed_inbox_created is True
    assert [warning.name for warning in response.warnings] == ['ERR_RUNTIME_UNAVAILABLE_NON_BLOCKING']
    assert [(message.inbox_kind, message.dispatch_status) for message in gateway.messages] == [
        ('agent_inbox', 'runtime_unavailable'),
        ('owner_copy', 'runtime_unavailable'),
    ]
    assert [(target, payload['method']) for target, payload in fanout.pushes] == [
        ('a_agent', 'hasn.message.received'),
        ('h_owner', 'hasn.message.received'),
        ('h_owner', 'hasn.runtime.warning'),
    ]


@pytest.mark.asyncio
async def test_runtime_dispatch_failure_after_accept_is_not_message_delivery_failure() -> None:
    runtime = RuntimeSummary(
        agent_hasn_id='a_agent',
        runtime_status='online',
        adapter_registered=True,
        handle_available=True,
        binding_id='rb_1',
        runtime_type='hermes',
        node_id='n_runtime',
        binding_node_id='n_runtime',
        presence='online',
    )
    gateway = GateAwareInMemoryGateway(
        recipients={'a_agent': Recipient('a_agent', 'agent', 'h_owner')},
        runtimes={'a_agent': runtime},
    )
    service = HasnMessageHubService(
        gateway=gateway,
        fanout=RecordingFanout(),
        runtime_dispatcher=FailingRuntimeDispatcher(),
        side_effect_dispatcher=NoopServerSideEffectDispatcher(),
    )

    response = await service.send(
        None,
        MessageHubSendRequest(
            owner_id='h_sender',
            envelope={'conversation_id': '00000000-0000-0000-0000-000000000102', 'to_id': 'a_agent'},
        ),
    )

    assert response.delivery_status == 'delivered'
    assert response.dispatch_status == 'dispatch_failed'
    assert response.suppressed_inbox_created is True
    assert [warning.name for warning in response.warnings] == ['ERR_RUNTIME_DISPATCH_FAILED_NON_BLOCKING']
    assert [(message.inbox_kind, message.dispatch_status) for message in gateway.messages] == [
        ('agent_inbox', 'dispatch_failed'),
        ('owner_copy', 'dispatch_failed'),
    ]

@dataclass
class CapturingSyncGateway:
    reports: list[dict[str, Any]] = field(default_factory=list)
    sync_events: list[Any] = field(default_factory=list)
    client_events: list[Any] = field(default_factory=list)
    namespace_revisions: dict[tuple[str, str, str], dict[str, Any]] = field(default_factory=dict)

    async def save_runtime_report(self, db: Any, report: dict[str, Any]) -> None:
        self.reports.append(report)

    async def pull_events(self, db: Any, *, owner_id: str, after_revision: int, limit: int) -> list[Any]:
        return [event for event in self.sync_events if event.revision > after_revision][:limit]

    async def save_client_event(self, db: Any, *, owner_id: str, node_id: str, event: Any) -> int | None:
        if event.event_type.startswith('memory.'):
            from backend.app.hasn.schema.hasn_sync import SyncEventRecord
            from backend.app.hasn.service.hasn_sync_service import _memory_namespace_revision_key

            sync_scope_kind, sync_scope_id, namespace = _memory_namespace_revision_key(event)
            revision_key = (sync_scope_kind, sync_scope_id, namespace)
            previous = self.namespace_revisions.get(revision_key)
            namespace_revision = int(previous['revision']) + 1 if previous else 1
            revision = len(self.sync_events) + 1
            event_id = f'se_memory_{revision}'
            payload = {
                **event.payload,
                'client_event_id': event.client_event_id,
                'node_id': node_id,
                'namespace_revision': namespace_revision,
            }
            self.sync_events.append(
                SyncEventRecord(
                    event_id=event_id,
                    event_type=event.event_type,
                    revision=revision,
                    created_at=datetime(2026, 5, 1, 9, revision, tzinfo=timezone.utc),
                    payload=payload,
                )
            )
            self.namespace_revisions[revision_key] = {'revision': namespace_revision, 'last_event_id': event_id}
            self.client_events.append((owner_id, node_id, event))
            return revision
        self.client_events.append((owner_id, node_id, event))
        return None


@pytest.mark.asyncio
async def test_runtime_report_accepts_redacted_summary_and_returns_sync_cursor() -> None:
    from backend.app.hasn.schema.hasn_sync import RuntimeReportRequest, RuntimeSummary, SyncEventRecord, SyncPullRequest
    from backend.app.hasn.service.hasn_sync_service import HasnSyncService

    gateway = CapturingSyncGateway(
        sync_events=[
            SyncEventRecord(
                event_id='se_1',
                event_type='runtime.reported',
                revision=4,
                created_at=datetime(2026, 5, 1, 9, tzinfo=timezone.utc),
                payload={'agent_id': 'a_agent'},
            )
        ]
    )
    service = HasnSyncService(gateway=gateway)

    report_response = await service.report_runtime(
        None,
        RuntimeReportRequest(
            owner_id='h_owner',
            node_id='n_runtime',
            runtime_summaries=[
                RuntimeSummary(
                    agent_id='a_agent',
                    binding_id='rb_1',
                    runtime_type='hermes',
                    status='online',
                    adapter_registered=True,
                    handle_available=True,
                    summary_json={'capability': 'chat'},
                )
            ],
        ),
    )
    pull_response = await service.pull(None, SyncPullRequest(owner_id='h_owner', cursor='owner:h_owner:3'))

    assert report_response.accepted == 1
    assert gateway.reports[0]['summary_json'] == {'capability': 'chat'}
    assert pull_response.next_cursor == 'owner:h_owner:4'
    assert [event.event_id for event in pull_response.events] == ['se_1']


@pytest.mark.asyncio
async def test_runtime_report_rejects_private_runtime_metadata() -> None:
    from backend.app.hasn.schema.hasn_sync import RuntimeReportRequest, RuntimeSummary
    from backend.app.hasn.service.hasn_sync_service import HasnSyncService

    service = HasnSyncService(gateway=CapturingSyncGateway())

    with pytest.raises(errors.RequestError, match='ERR_RUNTIME_PRIVATE_METADATA_REJECTED'):
        await service.report_runtime(
            None,
            RuntimeReportRequest(
                owner_id='h_owner',
                node_id='n_runtime',
                runtime_summaries=[
                    RuntimeSummary(
                        agent_id='a_agent',
                        binding_id='rb_1',
                        runtime_type='hermes',
                        status='online',
                        summary_json={'workspace_path': '/private/project'},
                    )
                ],
            ),
        )


@pytest.mark.asyncio
async def test_sync_push_memory_event_becomes_pullable_owner_sync_event() -> None:
    from backend.app.hasn.schema.hasn_sync import ClientEvent, SyncPullRequest, SyncPushRequest
    from backend.app.hasn.service.hasn_sync_service import HasnSyncService

    gateway = CapturingSyncGateway()
    service = HasnSyncService(gateway=gateway)

    push_response = await service.push(
        None,
        SyncPushRequest(
            owner_id='h_owner',
            node_id='n_runtime',
            events=[
                ClientEvent(
                    client_event_id='ce_memory_owner_portrait_1',
                    event_type='memory.owner_portrait.upserted',
                    hasn_id='h_owner',
                    dedupe_key='memory:owner_portrait:h_owner:1',
                    payload={
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_owner',
                        'namespace': 'portraits',
                        'record_id': 'owner_portrait:h_owner',
                        'revision': 1,
                    },
                )
            ],
        ),
    )
    pull_response = await service.pull(None, SyncPullRequest(owner_id='h_owner', cursor='owner:h_owner:0'))

    assert push_response.accepted == 1
    assert push_response.next_cursor == 'owner:h_owner:1'
    assert [event.event_type for event in pull_response.events] == ['memory.owner_portrait.upserted']
    assert pull_response.events[0].payload['namespace'] == 'portraits'
    assert pull_response.next_cursor == 'owner:h_owner:1'


@pytest.mark.asyncio
async def test_sync_push_memory_events_advance_namespace_revision_independently() -> None:
    from backend.app.hasn.schema.hasn_sync import ClientEvent, SyncPullRequest, SyncPushRequest
    from backend.app.hasn.service.hasn_sync_service import HasnSyncService

    gateway = CapturingSyncGateway()
    service = HasnSyncService(gateway=gateway)

    push_response = await service.push(
        None,
        SyncPushRequest(
            owner_id='h_owner',
            node_id='n_runtime',
            events=[
                ClientEvent(
                    client_event_id='ce_portrait_1',
                    event_type='memory.owner_portrait.upserted',
                    hasn_id='h_owner',
                    payload={
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_owner',
                        'namespace': 'portraits',
                        'record_id': 'owner_portrait:h_owner',
                        'revision': 1,
                    },
                ),
                ClientEvent(
                    client_event_id='ce_portrait_2',
                    event_type='memory.owner_portrait.upserted',
                    hasn_id='h_owner',
                    payload={
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_owner',
                        'namespace': 'portraits',
                        'record_id': 'owner_portrait:h_owner',
                        'revision': 2,
                    },
                ),
                ClientEvent(
                    client_event_id='ce_fact_1',
                    event_type='memory.owner_fact.upserted',
                    hasn_id='h_owner',
                    payload={
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_owner',
                        'namespace': 'facts',
                        'record_id': 'fact:h_owner:1',
                        'revision': 1,
                    },
                ),
            ],
        ),
    )
    pull_response = await service.pull(None, SyncPullRequest(owner_id='h_owner', cursor='owner:h_owner:0'))

    assert push_response.accepted == 3
    assert push_response.next_cursor == 'owner:h_owner:3'
    assert [event.revision for event in pull_response.events] == [1, 2, 3]
    assert [event.payload['namespace_revision'] for event in pull_response.events] == [1, 2, 1]
    assert gateway.namespace_revisions == {
        ('owner', 'h_owner', 'portraits'): {'revision': 2, 'last_event_id': 'se_memory_2'},
        ('owner', 'h_owner', 'facts'): {'revision': 1, 'last_event_id': 'se_memory_3'},
    }
    assert pull_response.events[1].payload['sync_scope_kind'] == 'owner'
    assert pull_response.events[1].payload['sync_scope_id'] == 'h_owner'
    assert pull_response.events[1].payload['namespace'] == 'portraits'
    assert pull_response.events[1].payload['record_id'] == 'owner_portrait:h_owner'


@pytest.mark.asyncio
async def test_sync_push_rejects_malformed_memory_event_without_scope_fields() -> None:
    from backend.app.hasn.schema.hasn_sync import ClientEvent, SyncPushRequest
    from backend.app.hasn.service.hasn_sync_service import HasnSyncService

    gateway = CapturingSyncGateway()
    service = HasnSyncService(gateway=gateway)

    push_response = await service.push(
        None,
        SyncPushRequest(
            owner_id='h_owner',
            node_id='n_runtime',
            events=[
                ClientEvent(
                    client_event_id='ce_bad_memory',
                    event_type='memory.owner_fact.upserted',
                    hasn_id='h_owner',
                    payload={'record_id': 'fact:h_owner:1'},
                ),
                ClientEvent(
                    client_event_id='ce_good_memory',
                    event_type='memory.owner_fact.upserted',
                    hasn_id='h_owner',
                    payload={
                        'sync_scope_kind': 'owner',
                        'sync_scope_id': 'h_owner',
                        'namespace': 'facts',
                        'record_id': 'fact:h_owner:2',
                        'revision': 1,
                    },
                ),
            ],
        ),
    )

    assert push_response.accepted == 1
    assert [error.name for error in push_response.rejected] == ['ERR_MEMORY_SYNC_SCOPE_INVALID']
    assert push_response.next_cursor == 'owner:h_owner:1'
    assert [event.client_event_id for _, _, event in gateway.client_events] == ['ce_good_memory']
    assert gateway.namespace_revisions == {
        ('owner', 'h_owner', 'facts'): {'revision': 1, 'last_event_id': 'se_memory_1'},
    }
