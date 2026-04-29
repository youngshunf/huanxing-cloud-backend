from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TestBase(DeclarativeBase):
    pass


class HermesAgentStub(TestBase):
    __tablename__ = 'hermes_agent'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(sa.String(64), unique=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger)
    agent_name: Mapped[str] = mapped_column(sa.String(64))
    template: Mapped[str] = mapped_column(sa.String(32), default='assistant')
    timezone: Mapped[str] = mapped_column(sa.String(64), default='Asia/Shanghai')
    status: Mapped[str] = mapped_column(sa.String(20), default='creating')
    runtime_id: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    runtime_profile_id: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    profile_name: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    llm_mode: Mapped[str] = mapped_column(sa.String(16), default='platform')
    llm_provider: Mapped[str] = mapped_column(sa.String(32), default='openai_compatible')
    llm_model: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    gateway_status: Mapped[str] = mapped_column(sa.String(20), default='stopped')
    workspace_status: Mapped[str] = mapped_column(sa.String(20), default='unknown')
    sandbox_status: Mapped[str] = mapped_column(sa.String(20), default='unknown')
    channel_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    last_active_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_runtime_sync_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    remark: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    deleted_time: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_time: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)


class HermesAgentRuntimeStateStub(TestBase):
    __tablename__ = 'hermes_agent_runtime_state'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(sa.String(64), unique=True)
    runtime_id: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    runtime_profile_id: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    profile_name: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    gateway_status: Mapped[str] = mapped_column(sa.String(20), default='stopped')
    gateway_restart_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    gateway_started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    api_server_reachable: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    terminal_backend: Mapped[str] = mapped_column(sa.String(16), default='docker')
    container_workspace: Mapped[str] = mapped_column(sa.String(64), default='/workspace')
    host_workspace_display: Mapped[str | None] = mapped_column(sa.String(256), nullable=True)
    workspace_status: Mapped[str] = mapped_column(sa.String(20), default='ready')
    workspace_file_count: Mapped[int] = mapped_column(sa.Integer, default=0)
    workspace_bytes_used: Mapped[int] = mapped_column(sa.BigInteger, default=0)
    workspace_last_write_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    mount_policy: Mapped[str] = mapped_column(sa.String(32), default='workspace_only')
    network_policy: Mapped[str] = mapped_column(sa.String(64), default='public_outbound_internal_denied')
    network_ready: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    runtime_snapshot: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    last_health_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)


class HermesAgentChannelBindingStub(TestBase):
    __tablename__ = 'hermes_agent_channel_binding'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    binding_id: Mapped[str] = mapped_column(sa.String(64))
    agent_id: Mapped[str] = mapped_column(sa.String(64))
    user_id: Mapped[int] = mapped_column(sa.BigInteger)
    channel: Mapped[str] = mapped_column(sa.String(20))
    bind_mode: Mapped[str] = mapped_column(sa.String(20), default='qr')
    status: Mapped[str] = mapped_column(sa.String(32), default='unbound')
    display_name: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    bound_account_display: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    runtime_session_id: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)


class HermesAgentOperationStub(TestBase):
    __tablename__ = 'hermes_agent_operation'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    operation_id: Mapped[str] = mapped_column(sa.String(64))
    agent_id: Mapped[str] = mapped_column(sa.String(64))
    user_id: Mapped[int] = mapped_column(sa.BigInteger)
    operation_type: Mapped[str] = mapped_column(sa.String(32))
    operation_status: Mapped[str] = mapped_column(sa.String(20))
    idempotency_key: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    runtime_request_id: Mapped[str | None] = mapped_column(sa.String(128), nullable=True)
    started_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    request_summary_json: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    response_summary_json: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    error_json: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)


class FakeRuntimeClient:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.calls: list[tuple[str, str | None, Any]] = []

    async def ensure_agent(self, payload, trace_id=None):
        self.calls.append(('ensure_agent', None, payload))
        if self.fail:
            from backend.app.hermes.service.hermes_runtime_client import HermesRuntimeError
            raise HermesRuntimeError(error='runtime_unavailable', details='connect timeout', action='retry later')
        return {
            'agent_id': payload['agent_id'],
            'runtime_profile_id': f"rtp_{payload['agent_id']}",
            'profile_name': f"rtp_{payload['agent_id']}",
            'container_workspace': '/workspace',
            'lifecycle_status': 'created',
            'updated_at': '2026-04-29T10:00:00+08:00',
        }

    async def put_soul(self, runtime_profile_id, content, trace_id=None):
        self.calls.append(('put_soul', runtime_profile_id, content))
        return {'kind': 'soul', 'updated_at': '2026-04-29T10:00:01+08:00', 'requires_gateway_restart': False}

    async def put_user_profile(self, runtime_profile_id, content, trace_id=None):
        self.calls.append(('put_user_profile', runtime_profile_id, content))
        return {'kind': 'user-profile', 'updated_at': '2026-04-29T10:00:02+08:00', 'requires_gateway_restart': False}

    async def start_gateway(self, runtime_profile_id, trace_id=None):
        self.calls.append(('start_gateway', runtime_profile_id, None))
        return {'status': 'running', 'api_server_host': '127.0.0.1', 'api_server_port': 18001}

    async def get_gateway_status(self, runtime_profile_id, trace_id=None):
        self.calls.append(('get_gateway_status', runtime_profile_id, None))
        return {'status': 'running', 'api_server_host': '127.0.0.1', 'api_server_port': 18001}


@pytest_asyncio.fixture
async def db_session(monkeypatch):
    import backend.app.hermes.service.hermes_agent_app_service as service_mod

    monkeypatch.setattr(service_mod, 'HermesAgent', HermesAgentStub, raising=True)
    monkeypatch.setattr(service_mod, 'HermesAgentRuntimeState', HermesAgentRuntimeStateStub, raising=True)
    monkeypatch.setattr(service_mod, 'HermesAgentChannelBinding', HermesAgentChannelBindingStub, raising=True)
    monkeypatch.setattr(service_mod, 'HermesAgentOperation', HermesAgentOperationStub, raising=True)

    class InMemorySession:
        def __init__(self):
            self.hermes_agents = []
            self.runtime_states = []
            self.channel_bindings = []
            self.operations = []
            self._ids = {}

        def add(self, obj):
            table = {
                HermesAgentStub: self.hermes_agents,
                HermesAgentRuntimeStateStub: self.runtime_states,
                HermesAgentChannelBindingStub: self.channel_bindings,
                HermesAgentOperationStub: self.operations,
            }[type(obj)]
            if getattr(obj, 'id', None) is None:
                nxt = self._ids.get(type(obj), 0) + 1
                self._ids[type(obj)] = nxt
                obj.id = nxt
            if obj not in table:
                table.append(obj)

        async def flush(self):
            return None

    return InMemorySession()


def _request(user_id: int):
    return SimpleNamespace(agent_name='福仔', template='assistant', timezone='Asia/Shanghai', soul='# SOUL', user_profile='# USER', auto_start_gateway=True)


@pytest.mark.asyncio
async def test_create_multiple_agents_for_one_user_saves_runtime_profile_and_uses_it_after_ensure(db_session):
    from backend.app.hermes.service.hermes_agent_app_service import HermesAgentAppService

    runtime = FakeRuntimeClient()
    service = HermesAgentAppService(runtime_client=runtime, id_factory=iter(['agt_a', 'agt_b']).__next__)

    first = await service.create_agent(db=db_session, user_id=1001, payload=_request(1001), trace_id='trace-a')
    second = await service.create_agent(db=db_session, user_id=1001, payload=_request(1001), trace_id='trace-b')

    assert first['agent_id'] == 'agt_a'
    assert second['agent_id'] == 'agt_b'
    assert first['status'] == 'running'
    assert 'runtime_profile_id' not in first
    assert 'profile_path' not in first
    assert ('put_soul', 'rtp_agt_a', '# SOUL') in runtime.calls
    assert ('put_user_profile', 'rtp_agt_a', '# USER') in runtime.calls
    assert ('start_gateway', 'rtp_agt_a', None) in runtime.calls


@pytest.mark.asyncio
async def test_user_isolation_hides_other_users_agent(db_session):
    from backend.app.hermes.service.hermes_agent_app_service import HermesAgentAppService
    from backend.common.exception import errors

    service = HermesAgentAppService(runtime_client=FakeRuntimeClient(), id_factory=lambda: 'agt_owner')
    await service.create_agent(db=db_session, user_id=1001, payload=_request(1001), trace_id='trace-owner')

    with pytest.raises(errors.NotFoundError):
        await service.get_agent_detail(db=db_session, user_id=2002, agent_id='agt_owner')

    mine = await service.list_agents(db=db_session, user_id=1001, page=1, size=20)
    other = await service.list_agents(db=db_session, user_id=2002, page=1, size=20)
    assert mine['total'] == 1
    assert other['total'] == 0


@pytest.mark.asyncio
async def test_runtime_unavailable_returns_structured_error_and_records_operation(db_session):
    from backend.app.hermes.service.hermes_agent_app_service import HermesAgentAppService
    from backend.app.hermes.service.hermes_runtime_client import HermesRuntimeError

    service = HermesAgentAppService(runtime_client=FakeRuntimeClient(fail=True), id_factory=lambda: 'agt_fail')

    with pytest.raises(HermesRuntimeError) as exc:
        await service.create_agent(db=db_session, user_id=1001, payload=_request(1001), trace_id='trace-fail')

    assert exc.value.to_response_data()['error'] == 'runtime_unavailable'
    ops = db_session.operations
    assert len(ops) == 1
    assert ops[0].operation_status == 'failed'
    assert ops[0].error_json['error'] == 'runtime_unavailable'
