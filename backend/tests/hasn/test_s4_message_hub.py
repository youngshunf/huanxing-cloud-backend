from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import pytest

from backend.app.hasn.schema.hasn_message_hub import InboxPullRequest, MessageHubSendRequest
from backend.app.hasn.service.hasn_message_hub_service import (
    HasnMessageHubService,
    MessageRecord,
    NoopServerSideEffectDispatcher,
    Recipient,
    RuntimeSummary,
    StoredMessage,
)

pytestmark = pytest.mark.asyncio

CONVERSATION_ID = '00000000-0000-0000-0000-000000000004'


@dataclass
class InMemoryS4Gateway:
    recipients: dict[str, Recipient]
    runtimes: dict[str, RuntimeSummary] = field(default_factory=dict)
    messages: list[StoredMessage] = field(default_factory=list)
    suppressed: list[StoredMessage] = field(default_factory=list)

    async def resolve_recipient(self, db: Any, target_hasn_id: str) -> Recipient | None:
        return self.recipients.get(target_hasn_id)

    async def store_inbox_message(self, db: Any, record: MessageRecord) -> StoredMessage:
        message = StoredMessage(
            message_id=str(len(self.messages) + 1),
            owner_id=record.owner_id,
            hasn_id=record.hasn_id,
            conversation_id=record.conversation_id,
            inbox_kind=record.inbox_kind,
            envelope=dict(record.envelope),
            dispatch_status=record.dispatch_status,
            created_at=datetime(2026, 4, 28, 4, 0, len(self.messages), tzinfo=timezone.utc),
        )
        self.messages.append(message)
        return message

    async def latest_runtime_summary(
        self, db: Any, *, owner_id: str, agent_hasn_id: str
    ) -> RuntimeSummary | None:
        return self.runtimes.get(agent_hasn_id)

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
        for message in self.messages:
            if message.message_id == message_id or message.inbox_kind == 'owner_copy':
                message.dispatch_status = dispatch_status

    async def pull_inbox(self, db: Any, request: InboxPullRequest, *, limit: int = 100):
        from backend.app.hasn.schema.hasn_message_hub import InboxItem, InboxPullResponse

        items = [
            InboxItem(
                message_id=m.message_id,
                owner_id=m.owner_id,
                hasn_id=m.hasn_id,
                conversation_id=m.conversation_id,
                inbox_kind=m.inbox_kind,
                envelope={**m.envelope, 'message_id': m.message_id, 'conversation_id': m.conversation_id},
                dispatch_status=m.dispatch_status,
                created_at=m.created_at,
            )
            for m in self.messages
            if m.owner_id == request.owner_id
        ]
        if request.include_suppressed:
            items.extend(
                InboxItem(
                    message_id=m.message_id,
                    owner_id=m.owner_id,
                    hasn_id=m.hasn_id,
                    conversation_id=m.conversation_id,
                    inbox_kind='suppressed_inbox',
                    envelope={**m.envelope, 'message_id': m.message_id, 'conversation_id': m.conversation_id},
                    dispatch_status=m.dispatch_status,
                    created_at=m.created_at,
                )
                for m in self.suppressed
                if m.owner_id == request.owner_id
            )
        items.sort(key=lambda item: (item.created_at, item.inbox_kind, item.message_id))
        return InboxPullResponse(
            items=items,
            next_cursor=f's4:{items[-1].message_id}' if items else 's4:0',
            has_more=False,
        )


@dataclass
class MultiNodeFanout:
    online_nodes: dict[str, list[str]] = field(default_factory=dict)
    pushes: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    delivered_nodes: dict[str, list[str]] = field(default_factory=dict)

    async def push(self, target_hasn_id: str, payload: dict[str, Any]) -> bool:
        self.pushes.append((target_hasn_id, payload))
        nodes = self.online_nodes.get(target_hasn_id, [])
        self.delivered_nodes.setdefault(target_hasn_id, []).extend(nodes)
        return bool(nodes)


@dataclass
class CapturingRuntimeDispatcher:
    calls: list[tuple[str, dict[str, Any], RuntimeSummary]] = field(default_factory=list)
    ok: bool = True

    async def dispatch(self, target_agent_id: str, payload: dict[str, Any], runtime: RuntimeSummary) -> bool:
        self.calls.append((target_agent_id, payload, runtime))
        return self.ok


class FailingSideEffectDispatcher(NoopServerSideEffectDispatcher):
    async def dispatch(self, envelope: dict[str, Any], message: StoredMessage) -> None:
        raise RuntimeError('side effect backend down')


def _service(gateway: InMemoryS4Gateway, fanout: MultiNodeFanout, runtime=None, side_effect=None):
    return HasnMessageHubService(
        gateway=gateway,
        fanout=fanout,
        runtime_dispatcher=runtime or CapturingRuntimeDispatcher(),
        side_effect_dispatcher=side_effect or NoopServerSideEffectDispatcher(),
    )


async def test_runtime_unavailable_agent_still_reaches_agent_owner_and_suppressed_inboxes() -> None:
    gateway = InMemoryS4Gateway(
        recipients={'a_agent': Recipient('a_agent', 'agent', 'h_owner', 'agent')},
    )
    fanout = MultiNodeFanout(online_nodes={'h_owner': ['node-a', 'node-b']})
    service = _service(gateway, fanout)

    response = await service.send(
        None,
        MessageHubSendRequest(
            owner_id='h_sender',
            envelope={
                'conversation_id': CONVERSATION_ID,
                'from_id': 'h_sender',
                'to_id': 'a_agent',
                'content': {'text': 'hello agent'},
            },
        ),
    )

    assert response.delivery_status == 'delivered'
    assert response.dispatch_status == 'runtime_unavailable'
    assert response.owner_copy_created is True
    assert response.suppressed_inbox_created is True
    assert [warning.name for warning in response.warnings] == ['ERR_RUNTIME_UNAVAILABLE_NON_BLOCKING']
    assert [(m.inbox_kind, m.owner_id, m.hasn_id, m.dispatch_status) for m in gateway.messages] == [
        ('agent_inbox', 'h_owner', 'a_agent', 'runtime_unavailable'),
        ('owner_copy', 'h_owner', 'h_owner', 'runtime_unavailable'),
    ]
    assert [m.inbox_kind for m in gateway.suppressed] == ['agent_inbox']
    assert [(target, payload['method']) for target, payload in fanout.pushes] == [
        ('a_agent', 'hasn.message.received'),
        ('h_owner', 'hasn.message.received'),
        ('h_owner', 'hasn.runtime.warning'),
    ]


async def test_owner_inbox_fanout_targets_owner_multi_node_route_without_runtime() -> None:
    gateway = InMemoryS4Gateway(
        recipients={'h_owner': Recipient('h_owner', 'human', 'h_owner', 'owner')},
    )
    fanout = MultiNodeFanout(online_nodes={'h_owner': ['desktop', 'web']})
    service = _service(gateway, fanout)

    response = await service.send(
        None,
        MessageHubSendRequest(
            owner_id='h_sender',
            envelope={
                'conversation_id': CONVERSATION_ID,
                'from_id': 'h_sender',
                'to_id': 'h_owner',
                'content': {'text': 'hello owner'},
            },
        ),
    )

    assert response.dispatch_status == 'not_required'
    assert response.owner_copy_created is False
    assert response.suppressed_inbox_created is False
    assert [(m.inbox_kind, m.owner_id, m.hasn_id) for m in gateway.messages] == [
        ('human_inbox', 'h_owner', 'h_owner')
    ]
    assert [target for target, _ in fanout.pushes] == ['h_owner']
    assert fanout.delivered_nodes['h_owner'] == ['desktop', 'web']


async def test_message_hub_rejects_invalid_card_before_persistence() -> None:
    gateway = InMemoryS4Gateway(
        recipients={'h_owner': Recipient('h_owner', 'human', 'h_owner', 'owner')},
    )
    fanout = MultiNodeFanout(online_nodes={'h_owner': ['desktop']})
    service = _service(gateway, fanout)

    with pytest.raises(Exception, match='Card message invalid'):
        await service.send(
            None,
            MessageHubSendRequest(
                owner_id='h_sender',
                envelope={
                    'conversation_id': CONVERSATION_ID,
                    'from_id': 'h_sender',
                    'to_id': 'h_owner',
                    'content_type': 'card',
                    'content': {
                        'schema_version': 'hasn.card/0.1',
                        'title': '非法卡片',
                        'source': {'kind': 'app', 'id': 'community', 'display_name': '社区'},
                        'resource': {
                            'type': 'community.post',
                            'id': 'post_01J',
                            'app_id': 'community',
                            'uri': 'javascript:alert(1)',
                        },
                        'primary_action': {
                            'label': '打开',
                            'action_id': 'open',
                            'kind': 'open_uri',
                            'uri': 'javascript:alert(1)',
                        },
                    },
                },
            ),
        )

    assert gateway.messages == []
    assert fanout.pushes == []


async def test_suppressed_inbox_pull_is_owner_multi_device_consistent_and_same_conversation() -> None:
    runtime = RuntimeSummary(
        agent_hasn_id='a_agent',
        runtime_status='online',
        adapter_registered=True,
        handle_available=True,
        binding_id='rb_1',
        runtime_type='hermes',
    )
    gateway = InMemoryS4Gateway(
        recipients={'a_agent': Recipient('a_agent', 'agent', 'h_owner', 'agent')},
        runtimes={'a_agent': runtime},
    )
    fanout = MultiNodeFanout(online_nodes={'h_owner': ['desktop', 'web']})
    service = _service(gateway, fanout, runtime=CapturingRuntimeDispatcher(ok=False))

    await service.send(
        None,
        MessageHubSendRequest(
            owner_id='h_sender',
            envelope={
                'conversation_id': CONVERSATION_ID,
                'from_id': 'h_sender',
                'to_id': 'a_agent',
                'content': {'text': 'needs runtime'},
                'node_role': 'observer-should-not-leak',
                'metadata': {'workspace': '/tmp/private', 'public_hint': 'ok'},
            },
        ),
    )

    first_device = await service.pull_inbox(None, InboxPullRequest(owner_id='h_owner', include_suppressed=True))
    second_device = await service.pull_inbox(None, InboxPullRequest(owner_id='h_owner', include_suppressed=True))

    assert first_device == second_device
    kinds = [item.inbox_kind for item in first_device.items]
    assert kinds == ['agent_inbox', 'suppressed_inbox', 'owner_copy']
    assert {item.conversation_id for item in first_device.items} == {CONVERSATION_ID}
    assert all('node_role' not in item.envelope for item in first_device.items)
    assert all('workspace' not in item.envelope.get('metadata', {}) for item in first_device.items)
    assert all(item.envelope.get('metadata', {}).get('public_hint') == 'ok' for item in first_device.items)
    assert all(item.envelope['conversation_id'] == CONVERSATION_ID for item in first_device.items)


async def test_online_runtime_dispatches_without_suppressed_inbox() -> None:
    runtime = RuntimeSummary(
        agent_hasn_id='a_agent',
        runtime_status='online',
        adapter_registered=True,
        handle_available=True,
        binding_id='rb_1',
        runtime_type='codex',
    )
    gateway = InMemoryS4Gateway(
        recipients={'a_agent': Recipient('a_agent', 'agent', 'h_owner', 'agent')},
        runtimes={'a_agent': runtime},
    )
    fanout = MultiNodeFanout(online_nodes={'a_agent': ['agent-node'], 'h_owner': ['owner-node']})
    runtime_dispatcher = CapturingRuntimeDispatcher()
    service = _service(gateway, fanout, runtime=runtime_dispatcher)

    response = await service.send(
        None,
        MessageHubSendRequest(
            owner_id='h_sender',
            envelope={
                'conversation_id': CONVERSATION_ID,
                'from_id': 'h_sender',
                'to_id': 'a_agent',
                'content': {'text': 'execute'},
            },
        ),
    )

    assert response.dispatch_status == 'dispatched'
    assert response.suppressed_inbox_created is False
    assert gateway.suppressed == []
    assert [call[0] for call in runtime_dispatcher.calls] == ['a_agent']


async def test_side_effect_dispatcher_failure_does_not_block_main_message_path() -> None:
    gateway = InMemoryS4Gateway(
        recipients={'h_owner': Recipient('h_owner', 'human', 'h_owner', 'owner')},
    )
    fanout = MultiNodeFanout(online_nodes={'h_owner': ['desktop']})
    service = _service(gateway, fanout, side_effect=FailingSideEffectDispatcher())

    response = await service.send(
        None,
        MessageHubSendRequest(
            owner_id='h_sender',
            envelope={
                'conversation_id': CONVERSATION_ID,
                'from_id': 'h_sender',
                'to_id': 'h_owner',
                'action': 'trade.accept',
                'content': {'trade_id': 't_1'},
            },
        ),
    )

    assert response.delivery_status == 'delivered'
    assert response.dispatch_status == 'not_required'
    assert fanout.pushes
