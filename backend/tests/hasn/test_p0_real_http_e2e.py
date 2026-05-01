from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from backend.app.hasn.api.v1 import message_hub as message_hub_api
from backend.app.hasn.api.v1 import onboarding as onboarding_api
from backend.app.hasn.api.v1 import sync as sync_api
from backend.app.hasn.schema.hasn_message_hub import InboxItem, InboxPullRequest, InboxPullResponse
from backend.app.hasn.schema.hasn_onboarding import SandboxSummary
from backend.app.hasn.service.hasn_message_hub_service import (
    HasnMessageHubService,
    MessageRecord,
    NoopServerSideEffectDispatcher,
    Recipient,
    RuntimeSummary as HubRuntimeSummary,
    StoredMessage,
)
from backend.app.hasn.service.hasn_onboarding_service import (
    DEFAULT_AGENT_DISPLAY_NAME,
    HasnOnboardingService,
    HasnPhoneAuthService,
    SMS_CODE_PREFIX,
)
from backend.app.hasn.service.hasn_sync_service import HasnSyncService
from backend.database.db import get_db, get_db_transaction


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
        return FakeUser(id=7, username=phone, nickname="P0 Dev User", phone=phone), True


class FakeDb:
    async def flush(self) -> None:
        return None


class FakeOnboardingGateway:
    async def get_user(self, _db: Any, user_id: int) -> FakeUser | None:
        if user_id != 7:
            return None
        return FakeUser(id=7, username="13800138000", nickname="P0 Dev User", phone="13800138000")

    async def ensure_human(self, _db: Any, user: FakeUser) -> tuple[Any, bool]:
        return SimpleNamespace(hasn_id="h_p0_owner", name=user.nickname), True

    async def ensure_node(self, _db: Any, _user_id: int, owner_id: str, request: Any) -> Any:
        assert owner_id == "h_p0_owner"
        assert "workspace_path" not in request.node.model_dump_json()
        return SimpleNamespace(node_id=request.node.node_id)

    async def ensure_owner_binding(self, _db: Any, node_id: str, owner_id: str) -> Any:
        return SimpleNamespace(node_id=node_id, owner_id=owner_id, status="active", sync_revision=1)

    async def ensure_default_agent(self, _db: Any, owner_id: str, node_id: str | None) -> tuple[Any, bool]:
        assert node_id == "n_p0_desktop"
        return SimpleNamespace(hasn_id="a_p0_default", owner_id=owner_id, name=DEFAULT_AGENT_DISPLAY_NAME), True

    async def consume_pending_intent(self, _db: Any, pending_intent_id: str, owner_id: str, agent_hasn_id: str) -> bool:
        assert (pending_intent_id, owner_id, agent_hasn_id) == ("pi_p0_real", "h_p0_owner", "a_p0_default")
        return True

    async def get_sandbox_summary(self, _db: Any, owner_id: str) -> SandboxSummary | None:
        assert owner_id == "h_p0_owner"
        return SandboxSummary(sandbox_id="sb_p0_owner", status="active", base_url=None)


@dataclass
class InMemorySyncGateway:
    reports: list[dict[str, Any]] = field(default_factory=list)
    client_events: list[Any] = field(default_factory=list)

    async def save_runtime_report(self, _db: Any, report: dict[str, Any]) -> None:
        self.reports.append(report)

    async def pull_events(self, _db: Any, *, owner_id: str, after_revision: int, limit: int) -> list[Any]:
        from backend.app.hasn.schema.hasn_sync import SyncEventRecord

        return [
            SyncEventRecord(
                event_id="se_runtime_reported",
                event_type="runtime.reported",
                revision=max(after_revision + 1, 1),
                created_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
                payload={"owner_id": owner_id, "reports": len(self.reports), "limit": limit},
            )
        ]

    async def save_client_event(self, _db: Any, *, owner_id: str, node_id: str, event: Any) -> None:
        self.client_events.append((owner_id, node_id, event))


@dataclass
class InMemoryMessageGateway:
    recipients: dict[str, Recipient]
    runtimes: dict[str, HubRuntimeSummary] = field(default_factory=dict)
    messages: list[StoredMessage] = field(default_factory=list)
    suppressed: list[StoredMessage] = field(default_factory=list)

    async def resolve_recipient(self, _db: Any, target_hasn_id: str) -> Recipient | None:
        return self.recipients.get(target_hasn_id)

    async def latest_runtime_summary(self, _db: Any, *, owner_id: str, agent_hasn_id: str) -> HubRuntimeSummary | None:
        assert owner_id == "h_p0_owner"
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
        assert runtime_summary and runtime_summary.runtime_type == "hermes"
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
                    message_id=f"suppressed:{message.message_id}",
                    owner_id=message.owner_id,
                    hasn_id=message.hasn_id,
                    conversation_id=message.conversation_id,
                    inbox_kind="suppressed_inbox",
                    dispatch_status=message.dispatch_status,
                    created_at=message.created_at,
                    envelope=message.envelope,
                )
                for message in self.suppressed
            )
        return InboxPullResponse(items=items, next_cursor=f"owner:{request.owner_id}:{len(items)}", has_more=False)


class RecordingFanout:
    def __init__(self) -> None:
        self.pushes: list[tuple[str, dict[str, Any]]] = []

    async def push(self, target_hasn_id: str, payload: dict[str, Any]) -> bool:
        self.pushes.append((target_hasn_id, payload))
        return True


class FailingRuntimeDispatcher:
    async def dispatch(self, target_agent_id: str, payload: dict[str, Any], runtime: HubRuntimeSummary) -> bool:
        assert target_agent_id == "a_p0_default"
        assert runtime.runtime_type == "hermes"
        assert payload["method"] == "hasn.message.received"
        return False


def make_app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    app = FastAPI()
    app.include_router(onboarding_api.router, prefix="/api/v1/hasn")
    app.include_router(sync_api.router, prefix="/api/v1/hasn")
    app.include_router(message_hub_api.router, prefix="/api/v1/hasn")

    async def fake_db():
        yield FakeDb()

    app.dependency_overrides[get_db] = fake_db
    app.dependency_overrides[get_db_transaction] = fake_db
    monkeypatch.setattr(onboarding_api, "jwt_decode", lambda _token: SimpleNamespace(id=7))

    async def fake_token_creator(*_args: Any, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(access_token="jwt-p0-real-http")

    redis = FakeRedis()
    phone_auth = HasnPhoneAuthService(
        redis=redis,
        sms=FakeSms(),
        users=FakeUserGateway(),
        code_generator=lambda: "123456",
        token_creator=fake_token_creator,
    )
    monkeypatch.setattr(onboarding_api, "hasn_phone_auth_service", phone_auth)
    monkeypatch.setattr(onboarding_api, "hasn_onboarding_service", HasnOnboardingService(gateway=FakeOnboardingGateway()))

    sync_gateway = InMemorySyncGateway()
    monkeypatch.setattr(sync_api, "hasn_sync_service", HasnSyncService(gateway=sync_gateway))

    message_gateway = InMemoryMessageGateway(
        recipients={
            "h_p0_owner": Recipient("h_p0_owner", "human", "h_p0_owner"),
            "a_p0_default": Recipient("a_p0_default", "agent", "h_p0_owner"),
        },
        runtimes={
            "a_p0_default": HubRuntimeSummary(
                agent_hasn_id="a_p0_default",
                runtime_status="online",
                adapter_registered=True,
                handle_available=True,
                binding_id="bind_p0_default",
                runtime_type="hermes",
                node_id="n_p0_desktop",
                binding_node_id="n_p0_desktop",
                presence="online",
            )
        },
    )
    monkeypatch.setattr(
        message_hub_api,
        "hasn_message_hub_service",
        HasnMessageHubService(
            gateway=message_gateway,
            fanout=RecordingFanout(),
            runtime_dispatcher=FailingRuntimeDispatcher(),
            side_effect_dispatcher=NoopServerSideEffectDispatcher(),
        ),
    )

    redis.values[f"{SMS_CODE_PREFIX}:13800138000"] = "123456"
    return app


def test_p0_real_http_flow_covers_auth_onboarding_sync_runtime_report_message_and_inbox(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(make_app(monkeypatch))
    auth = {"Authorization": "Bearer jwt-p0-real-http"}

    assert client.post("/api/v1/hasn/auth/phone/send_code", json={"phone": "13800138000"}).status_code == 200
    verify = client.post(
        "/api/v1/hasn/auth/phone/verify",
        json={"phone": "13800138000", "code": "123456", "pending_intent_id": "pi_p0_real"},
    )
    assert verify.status_code == 200
    assert verify.json()["access_token"] == "jwt-p0-real-http"

    onboarding = client.post(
        "/api/v1/hasn/onboarding/ensure",
        headers=auth,
        json={
            "node": {
                "node_id": "n_p0_desktop",
                "device_name": "P0 Desktop",
                "platform": "macos",
                "client_version": "p0-real-http",
            },
            "client": {"protocol": "hasn/0.2", "supported_extensions": ["sync.pull", "message_hub"]},
            "pending_intent_id": "pi_p0_real",
        },
    )
    assert onboarding.status_code == 200
    assert onboarding.json()["human"]["owner_id"] == "h_p0_owner"
    assert onboarding.json()["default_agent"]["hasn_id"] == "a_p0_default"

    runtime_report = client.post(
        "/api/v1/hasn/runtime/report",
        headers=auth,
        json={
            "owner_id": "h_p0_owner",
            "node_id": "n_p0_desktop",
            "runtime_summaries": [
                {
                    "agent_id": "a_p0_default",
                    "binding_id": "bind_p0_default",
                    "runtime_type": "hermes",
                    "status": "online",
                    "adapter_registered": True,
                    "handle_available": True,
                    "summary_json": {"capability": "dispatch"},
                }
            ],
        },
    )
    assert runtime_report.status_code == 200
    assert runtime_report.json()["accepted"] == 1

    sync_push = client.post(
        "/api/v1/hasn/sync/push",
        headers=auth,
        json={
            "owner_id": "h_p0_owner",
            "node_id": "n_p0_desktop",
            "events": [{"client_event_id": "ce_1", "event_type": "node.session", "payload": {"status": "ready"}}],
        },
    )
    assert sync_push.status_code == 200
    assert sync_push.json()["accepted"] == 1

    human_message = client.post(
        "/api/v1/hasn/messages/send",
        headers=auth,
        json={"owner_id": "h_p0_owner", "envelope": {"conversation_id": "00000000-0000-0000-0000-000000000201", "to_id": "h_p0_owner"}},
    )
    assert human_message.status_code == 200
    assert human_message.json()["delivery_status"] == "delivered"
    assert human_message.json()["dispatch_status"] == "not_required"

    agent_message = client.post(
        "/api/v1/hasn/messages/send",
        headers=auth,
        json={"owner_id": "h_sender", "envelope": {"conversation_id": "00000000-0000-0000-0000-000000000202", "to_id": "a_p0_default"}},
    )
    assert agent_message.status_code == 200
    assert agent_message.json()["delivery_status"] == "delivered"
    assert agent_message.json()["dispatch_status"] == "dispatch_failed"
    assert agent_message.json()["suppressed_inbox_created"] is True
    assert agent_message.json()["warnings"][0]["name"] == "ERR_RUNTIME_DISPATCH_FAILED_NON_BLOCKING"

    inbox = client.post(
        "/api/v1/hasn/inbox/pull",
        headers=auth,
        json={"owner_id": "h_p0_owner", "include_suppressed": True},
    )
    assert inbox.status_code == 200
    inbox_kinds = [item["inbox_kind"] for item in inbox.json()["items"]]
    assert "human_inbox" in inbox_kinds
    assert "agent_inbox" in inbox_kinds
    assert "owner_copy" in inbox_kinds
    assert "suppressed_inbox" in inbox_kinds
