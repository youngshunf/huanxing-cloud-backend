"""单测：HermesAgentAppService.create_agent BYOK fast-fail
+ _resolve_template marketplace 查询（M1 §5.2 sub-tasks a + b）。

风格 mirror backend/tests/hermes/test_agent_app_service.py：使用 SimpleNamespace
+ InMemorySession-style stub，避免真连 PostgreSQL。
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest

from backend.app.hermes.service.hermes_agent_app_service import HermesAgentAppService
from backend.common.exception import errors


class _MarketplaceAppStub:
    def __init__(self, **kw: Any) -> None:
        for k, v in kw.items():
            setattr(self, k, v)


class _MarketplaceAppVersionStub:
    def __init__(self, **kw: Any) -> None:
        for k, v in kw.items():
            setattr(self, k, v)


class _MarketplaceSession:
    """Minimal stub session that the service's hasattr-branch picks up."""

    def __init__(self) -> None:
        self.marketplace_apps: list[_MarketplaceAppStub] = []
        self.marketplace_app_versions: list[_MarketplaceAppVersionStub] = []

    async def flush(self) -> None:
        return None

    def add(self, _obj: Any) -> None:
        return None


def _byok_payload() -> SimpleNamespace:
    return SimpleNamespace(
        agent_name='福仔',
        template='pet-sitter',
        timezone='Asia/Shanghai',
        soul=None,
        user_profile=None,
        auto_start_gateway=False,
        llm_mode='byok',
    )


@pytest.mark.asyncio
async def test_create_agent_rejects_byok_mode_with_request_error():
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_byok')
    with pytest.raises(errors.RequestError) as exc_info:
        await service.create_agent(db=_MarketplaceSession(), user_id=1001, payload=_byok_payload())
    assert 'BYOK' in exc_info.value.msg or 'byok' in exc_info.value.msg.lower()
    assert 'platform' in exc_info.value.msg


@pytest.mark.asyncio
async def test_resolve_template_happy_path_returns_version_and_package_metadata():
    db = _MarketplaceSession()
    db.marketplace_apps.append(
        _MarketplaceAppStub(
            app_id='pet-sitter',
            app_type='agent_template',
            name='宠物管家',
            description='帮你照顾家里的宠物',
            emoji='🐾',
            icon_url='https://cdn.example.com/pet-sitter.png',
            skill_dependencies='skill-feed,skill-vet',
        )
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(
            app_id='pet-sitter',
            version='v1.2.0',
            package_url='https://cdn.example.com/pet-sitter-v1.2.0.tar.gz',
            file_hash='sha256:abc123',
            is_latest=True,
            published_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        )
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(
            app_id='pet-sitter',
            version='v1.0.0',
            package_url='https://cdn.example.com/pet-sitter-v1.0.0.tar.gz',
            file_hash='sha256:old',
            is_latest=False,
        )
    )

    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    result = await service._resolve_template(db, 'pet-sitter')

    assert result['app_id'] == 'pet-sitter'
    assert result['version'] == 'v1.2.0'
    assert result['package_url'].endswith('pet-sitter-v1.2.0.tar.gz')
    assert result['file_hash'] == 'sha256:abc123'
    assert result['name'] == '宠物管家'
    assert result['emoji'] == '🐾'


@pytest.mark.asyncio
async def test_resolve_template_raises_when_app_missing():
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError) as exc_info:
        await service._resolve_template(_MarketplaceSession(), 'unknown-template')
    assert exc_info.value.msg == 'template_not_found'


@pytest.mark.asyncio
async def test_resolve_template_raises_when_no_latest_version_published():
    db = _MarketplaceSession()
    db.marketplace_apps.append(
        _MarketplaceAppStub(app_id='media-creator', app_type='agent_template', name='Media Creator')
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(
            app_id='media-creator', version='v0.1.0', is_latest=False, package_url='x', file_hash='y'
        )
    )
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError) as exc_info:
        await service._resolve_template(db, 'media-creator')
    assert exc_info.value.msg == 'template_not_found'


@pytest.mark.asyncio
async def test_resolve_template_filters_out_skill_pack_apps():
    """app_type='skill_pack' 不能被当成模板用（即使 app_id 撞名）。"""
    db = _MarketplaceSession()
    db.marketplace_apps.append(
        _MarketplaceAppStub(app_id='skill-imposter', app_type='skill_pack', name='Skill Pack')
    )
    db.marketplace_app_versions.append(
        _MarketplaceAppVersionStub(app_id='skill-imposter', version='v1', is_latest=True, package_url='', file_hash='')
    )
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError):
        await service._resolve_template(db, 'skill-imposter')


@pytest.mark.asyncio
async def test_resolve_template_with_empty_template_id_raises():
    service = HermesAgentAppService(runtime_client=object(), id_factory=lambda: 'agt_x')
    with pytest.raises(errors.NotFoundError):
        await service._resolve_template(_MarketplaceSession(), '')


# ----- §5.2 (d) ensure_agent_token + install_credential 串接 -----


class _FullSession(_MarketplaceSession):
    """Mirror backend/tests/hermes InMemorySession—supports hermes_agents/runtime_states
    so service.create_agent can persist locally without PostgreSQL.
    """

    def __init__(self) -> None:
        super().__init__()
        self.hermes_agents: list[Any] = []
        self.runtime_states: list[Any] = []
        self.channel_bindings: list[Any] = []
        self.operations: list[Any] = []
        self._auto_id = 0
        # Seed default 'assistant' template
        self.marketplace_apps.append(
            _MarketplaceAppStub(app_id='assistant', app_type='agent_template', name='通用助理')
        )
        self.marketplace_app_versions.append(
            _MarketplaceAppVersionStub(
                app_id='assistant',
                version='v1.0.0',
                package_url='https://cdn.example.com/assistant-v1.0.0.tar.gz',
                file_hash='sha256:fake',
                is_latest=True,
            )
        )

    def add(self, obj: Any) -> None:
        # 模拟 SQLAlchemy add：根据 type 路由到对应 list
        cls = type(obj).__name__
        if cls == 'HermesAgent':
            self.hermes_agents.append(obj)
        elif cls == 'HermesAgentRuntimeState':
            self.runtime_states.append(obj)
        elif cls == 'HermesAgentChannelBinding':
            self.channel_bindings.append(obj)
        elif cls == 'HermesAgentOperation':
            self.operations.append(obj)


class _FullRuntimeClient:
    def __init__(self, *, install_credential_fail: bool = False) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.install_credential_fail = install_credential_fail

    async def ensure_agent(self, payload, trace_id=None):
        self.calls.append(('ensure_agent', payload))
        return {
            'agent_id': payload['agent_id'],
            'runtime_profile_id': f"rtp_{payload['agent_id']}",
            'profile_name': f"rtp_{payload['agent_id']}",
            'container_workspace': '/workspace',
        }

    async def apply_template(self, runtime_profile_id, payload, trace_id=None):
        self.calls.append(('apply_template', {'profile_id': runtime_profile_id, **payload}))
        return {'status': 'rendered'}

    async def install_credential(self, runtime_profile_id, payload, trace_id=None):
        self.calls.append(('install_credential', {'profile_id': runtime_profile_id, **payload}))
        if self.install_credential_fail:
            from backend.app.hermes.service.hermes_runtime_client import HermesRuntimeError
            raise HermesRuntimeError(error='runtime_busy', details='quota exceeded', status_code=503)
        return {'installed': True}

    async def delete_agent(self, runtime_profile_id, trace_id=None):
        self.calls.append(('delete_agent', runtime_profile_id))
        return {'deleted': True}

    async def put_soul(self, runtime_profile_id, content, trace_id=None):
        self.calls.append(('put_soul', content))
        return {}

    async def put_user_profile(self, runtime_profile_id, content, trace_id=None):
        self.calls.append(('put_user_profile', content))
        return {}

    async def start_gateway(self, runtime_profile_id, trace_id=None):
        self.calls.append(('start_gateway', runtime_profile_id))
        return {'status': 'running'}


def _full_payload() -> SimpleNamespace:
    return SimpleNamespace(
        agent_name='福仔',
        template='assistant',
        timezone='Asia/Shanghai',
        soul=None,
        user_profile=None,
        auto_start_gateway=False,
        llm_mode='platform',
    )


@pytest.mark.asyncio
async def test_create_agent_with_newapi_db_calls_ensure_agent_token_and_installs_credential(monkeypatch):
    """Full happy path: ensure_agent → apply_template → ensure_agent_token →
    install_credential，且 install_credential 收到 sk-* 前缀的 token_key。
    """
    issued_calls: list[dict[str, Any]] = []

    async def _fake_ensure_agent_token(db, newapi_db, *, agent_id, user_id, **kw):
        issued_calls.append({'agent_id': agent_id, 'user_id': user_id, **kw})
        return {
            'agent_id': agent_id,
            'newapi_user_id': 100001,
            'newapi_token_id': 200001,
            'token_key_prefix': 'hxTESTON',
            'raw_token_key': 'hxTESTONLYabcdefghijklmnop1234567890abcdefghij',
            'reused': False,
        }

    from backend.app.hermes.service import hermes_agent_app_service as svc_mod

    monkeypatch.setattr(
        svc_mod.LlmNewapiUserMappingService, 'ensure_agent_token', staticmethod(_fake_ensure_agent_token)
    )

    db = _FullSession()
    newapi_db = _FullSession()
    runtime = _FullRuntimeClient()
    service = HermesAgentAppService(runtime_client=runtime, id_factory=lambda: 'agt_full')

    result = await service.create_agent(
        db=db, user_id=1001, payload=_full_payload(), trace_id='trace-1', newapi_db=newapi_db
    )

    call_names = [c[0] for c in runtime.calls]
    # 顺序断言：ensure_agent → apply_template → install_credential
    assert call_names.index('ensure_agent') < call_names.index('apply_template')
    assert call_names.index('apply_template') < call_names.index('install_credential')

    assert len(issued_calls) == 1
    assert issued_calls[0]['agent_id'] == 'agt_full'
    assert issued_calls[0]['user_id'] == 1001

    install_call = next(c for c in runtime.calls if c[0] == 'install_credential')
    assert install_call[1]['token_key'].startswith('sk-hxTESTONLY')
    assert install_call[1]['default_model']  # 非空
    assert 'base_url' in install_call[1]

    # 返回 card 含 template_version
    assert result['template_version'] == 'v1.0.0'
    assert result['template'] == 'assistant'


@pytest.mark.asyncio
async def test_create_agent_install_credential_failure_triggers_rollback(monkeypatch):
    """install_credential 失败 → 调用 revoke_agent_token + runtime.delete_agent
    （皆 swallow 不阻断主异常）。
    """
    revoke_calls: list[str] = []

    async def _fake_ensure_agent_token(db, newapi_db, *, agent_id, user_id, **kw):
        return {
            'agent_id': agent_id,
            'newapi_user_id': 100001,
            'newapi_token_id': 200001,
            'token_key_prefix': 'hxROLLBK',
            'raw_token_key': 'hxROLLBKabcdefghijklmnop1234567890abcdefghij',
            'reused': False,
        }

    async def _fake_revoke_agent_token(db, newapi_db, agent_id):
        revoke_calls.append(agent_id)
        return True

    from backend.app.hermes.service import hermes_agent_app_service as svc_mod

    monkeypatch.setattr(
        svc_mod.LlmNewapiUserMappingService, 'ensure_agent_token', staticmethod(_fake_ensure_agent_token)
    )
    monkeypatch.setattr(
        svc_mod.LlmNewapiUserMappingService, 'revoke_agent_token', staticmethod(_fake_revoke_agent_token)
    )

    db = _FullSession()
    newapi_db = _FullSession()
    runtime = _FullRuntimeClient(install_credential_fail=True)
    service = HermesAgentAppService(runtime_client=runtime, id_factory=lambda: 'agt_rb')

    from backend.app.hermes.service.hermes_runtime_client import HermesRuntimeError

    with pytest.raises(HermesRuntimeError):
        await service.create_agent(
            db=db, user_id=1001, payload=_full_payload(), trace_id='trace-rb', newapi_db=newapi_db
        )

    # 回滚链都被调
    assert revoke_calls == ['agt_rb']
    call_names = [c[0] for c in runtime.calls]
    assert 'delete_agent' in call_names


# ----- §5.3 delete_agent reverse cleanup -----


class _DeleteRuntimeClient(_FullRuntimeClient):
    def __init__(self, *, stop_gateway_fail: bool = False, runtime_delete_fail: bool = False) -> None:
        super().__init__()
        self.stop_gateway_fail = stop_gateway_fail
        self.runtime_delete_fail = runtime_delete_fail

    async def stop_gateway(self, runtime_profile_id, trace_id=None):
        self.calls.append(('stop_gateway', runtime_profile_id))
        if self.stop_gateway_fail:
            from backend.app.hermes.service.hermes_runtime_client import HermesRuntimeError
            raise HermesRuntimeError(error='gateway_already_stopped', details='not running')
        return {'status': 'stopped'}

    async def uninstall_credential(self, runtime_profile_id, trace_id=None):
        self.calls.append(('uninstall_credential', runtime_profile_id))
        return {'removed': True}

    async def delete_agent(self, runtime_profile_id, trace_id=None):
        self.calls.append(('delete_agent', runtime_profile_id))
        if self.runtime_delete_fail:
            from backend.app.hermes.service.hermes_runtime_client import HermesRuntimeError
            raise HermesRuntimeError(error='profile_not_found', status_code=404)
        return {'deleted': True}


async def _seed_existing_agent(db: _FullSession, agent_id: str = 'agt_del') -> str:
    """Helper：直接在 InMemorySession 里建一个 'created' 状态的 agent stub，
    避开 create_agent 全流程，专测 delete_agent。
    """
    agent = SimpleNamespace(
        agent_id=agent_id,
        user_id=1001,
        agent_name='福仔删除测试',
        template='assistant',
        runtime_profile_id=f'rtp_{agent_id}',
        runtime_id='hermes-runtime-local',
        profile_name=f'rtp_{agent_id}',
        status='running',
        gateway_status='running',
        workspace_status='active',
        sandbox_status='ready',
        deleted_time=None,
        last_error_code=None,
        last_error_message=None,
        last_active_at=None,
        last_runtime_sync_at=None,
        timezone='Asia/Shanghai',
        llm_mode='platform',
        llm_provider='openai_compatible',
        llm_model='openai/gpt-5.5',
        created_time=datetime(2026, 5, 1, tzinfo=timezone.utc),
        updated_time=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )
    db.hermes_agents.append(agent)
    return agent_id


@pytest.mark.asyncio
async def test_delete_agent_reverse_cleanup_calls_all_steps_in_order(monkeypatch):
    revoke_calls: list[str] = []

    async def _fake_revoke(db, newapi_db, agent_id):
        revoke_calls.append(agent_id)
        return True

    from backend.app.hermes.service import hermes_agent_app_service as svc_mod
    monkeypatch.setattr(
        svc_mod.LlmNewapiUserMappingService, 'revoke_agent_token', staticmethod(_fake_revoke)
    )

    db = _FullSession()
    newapi_db = _FullSession()
    runtime = _DeleteRuntimeClient()
    service = HermesAgentAppService(runtime_client=runtime, id_factory=lambda: 'agt_del')
    await _seed_existing_agent(db)

    result = await service.delete_agent(
        db=db, user_id=1001, agent_id='agt_del', trace_id='trace-del', newapi_db=newapi_db,
    )

    assert result['status'] == 'deleted'
    call_names = [c[0] for c in runtime.calls]
    # 顺序：stop_gateway → uninstall_credential → delete_agent
    assert call_names.index('stop_gateway') < call_names.index('uninstall_credential')
    assert call_names.index('uninstall_credential') < call_names.index('delete_agent')
    assert revoke_calls == ['agt_del']
    assert db.hermes_agents[0].deleted_time is not None
    assert db.hermes_agents[0].gateway_status == 'stopped'


@pytest.mark.asyncio
async def test_delete_agent_swallows_stop_gateway_failure_and_continues_cleanup(monkeypatch):
    revoke_calls: list[str] = []

    async def _fake_revoke(db, newapi_db, agent_id):
        revoke_calls.append(agent_id)
        return True

    from backend.app.hermes.service import hermes_agent_app_service as svc_mod
    monkeypatch.setattr(
        svc_mod.LlmNewapiUserMappingService, 'revoke_agent_token', staticmethod(_fake_revoke)
    )

    db = _FullSession()
    newapi_db = _FullSession()
    runtime = _DeleteRuntimeClient(stop_gateway_fail=True)
    service = HermesAgentAppService(runtime_client=runtime, id_factory=lambda: 'agt_del')
    await _seed_existing_agent(db)

    result = await service.delete_agent(
        db=db, user_id=1001, agent_id='agt_del', trace_id='trace-del', newapi_db=newapi_db,
    )

    # stop_gateway 失败不阻断；后续步骤仍执行
    assert result['status'] == 'deleted'
    assert revoke_calls == ['agt_del']
    assert 'delete_agent' in [c[0] for c in runtime.calls]
    assert db.hermes_agents[0].deleted_time is not None


@pytest.mark.asyncio
async def test_delete_agent_without_newapi_db_skips_token_revocation():
    """endpoint 兼容路径（旧调用方未传 newapi_db）不应崩溃。"""
    db = _FullSession()
    runtime = _DeleteRuntimeClient()
    service = HermesAgentAppService(runtime_client=runtime, id_factory=lambda: 'agt_del')
    await _seed_existing_agent(db)

    result = await service.delete_agent(
        db=db, user_id=1001, agent_id='agt_del', trace_id='trace-del'
    )
    assert result['status'] == 'deleted'
    # 没传 newapi_db → revoke_agent_token 不被调（service 没去 import 失败）
    assert db.hermes_agents[0].deleted_time is not None
