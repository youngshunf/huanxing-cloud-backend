from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

import pytest
import pytest_asyncio


class _StubBase:
    id: int | None = None
    created_time: datetime
    updated_time: datetime | None = None

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.id = kwargs.get('id')
        self.created_time = kwargs.get('created_time', datetime.now(timezone.utc))
        self.updated_time = kwargs.get('updated_time')


class HermesAgentStub(_StubBase):
    deleted_time = None
    last_active_at = None
    last_runtime_sync_at = None
    last_error_code = None
    last_error_message = None
    runtime_profile_id = None
    profile_name = None
    runtime_id = None


class HermesAgentRuntimeStateStub(_StubBase):
    pass


class HermesAgentChannelBindingStub(_StubBase):
    updated_time = None


class HermesAgentOperationStub(_StubBase):
    pass


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
        return {
            'status': 'running',
            'api_server_host': '127.0.0.1',
            'api_server_port': 18001,
            'started_at': '2026-04-29T10:03:00+08:00',
        }

    async def get_gateway_status(self, runtime_profile_id, trace_id=None):
        self.calls.append(('get_gateway_status', runtime_profile_id, None))
        return {'status': 'running', 'api_server_host': '127.0.0.1', 'api_server_port': 18001}

    async def get_workspace_status(self, runtime_profile_id, trace_id=None):
        self.calls.append(('get_workspace_status', runtime_profile_id, None))
        return {
            'profile_id': runtime_profile_id,
            'workspace_path': f'/tmp/hermes/workspaces/{runtime_profile_id}',
            'container_workspace': '/workspace',
            'status': 'active',
            'file_count': 2,
            'bytes_used': 128,
            'last_write_at': '2026-04-29T10:05:00+00:00',
        }

    async def chat_completions(self, runtime_profile_id, payload, trace_id=None):
        self.calls.append(('chat_completions', runtime_profile_id, payload))
        return {'id': 'chatcmpl_test', 'choices': [{'message': {'role': 'assistant', 'content': 'ok'}}]}

    async def get_channels(self, runtime_profile_id, trace_id=None):
        self.calls.append(('get_channels', runtime_profile_id, None))
        return {
            'profile_id': runtime_profile_id,
            'channels': [
                {'channel': 'feishu', 'status': 'bound', 'metadata': {'account_display': 'ou_****1001'}},
                {'channel': 'weixin', 'status': 'unbound', 'metadata': {}},
            ],
        }


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
    assert db_session.runtime_states[0].gateway_started_at == datetime(
        2026, 4, 29, 10, 3, tzinfo=timezone(timedelta(hours=8))
    )


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


@pytest.mark.asyncio
async def test_channels_shape_matches_website_contract_and_chat_syncs_workspace_state(db_session):
    from backend.app.hermes.service.hermes_agent_app_service import HermesAgentAppService

    runtime = FakeRuntimeClient()
    service = HermesAgentAppService(runtime_client=runtime, id_factory=lambda: 'agt_sync')
    await service.create_agent(db=db_session, user_id=1001, payload=_request(1001), trace_id='trace-create')

    channels = await service.channels(db=db_session, user_id=1001, agent_id='agt_sync', trace_id='trace-channels')
    assert isinstance(channels, list)
    assert channels[0]['channel'] == 'feishu'
    assert channels[0]['display_name'] == '飞书'
    assert channels[0]['bound_account_display'] == 'ou_****1001'

    chat = await service.chat_completions(
        db=db_session,
        user_id=1001,
        agent_id='agt_sync',
        payload={'messages': [{'role': 'user', 'content': 'hello'}]},
        trace_id='trace-chat',
    )
    assert chat['id'] == 'chatcmpl_test'
    state = db_session.runtime_states[0]
    assert state.workspace_status == 'active'
    assert state.workspace_file_count == 2
    assert state.workspace_bytes_used == 128
    assert state.host_workspace_display == '/data/huanxing-hermes/workspaces/agt_sync'
