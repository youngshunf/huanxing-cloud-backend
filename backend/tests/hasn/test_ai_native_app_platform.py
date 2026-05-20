from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_ai_native_codegen_and_migration_foundation_exist() -> None:
    expected = {
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'migration' / 'v12_ai_native_app_platform.sql',
        REPO_ROOT / 'backend' / 'sql' / 'hasn' / 'hasn_ai_native_app_manifest.sql',
        REPO_ROOT / 'backend' / 'sql' / 'hasn' / 'hasn_ai_native_app_audit.sql',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'model' / 'hasn_ai_native_app_manifest.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'model' / 'hasn_ai_native_app_audit.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'crud' / 'crud_hasn_ai_native_app_manifest.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'crud' / 'crud_hasn_ai_native_app_audit.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'schema' / 'ai_native_app.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'schema' / 'ai_native_runtime.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'schema' / 'ai_native_audit.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'service' / 'ai_native_builtin_manifests.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'service' / 'ai_native_app_registry.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'service' / 'ai_native_runtime_gateway.py',
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'service' / 'ai_native_audit_service.py',
    }

    missing = [path.relative_to(REPO_ROOT).as_posix() for path in expected if not path.exists()]

    assert missing == []


def test_legacy_app_platform_backend_surface_is_removed() -> None:
    legacy_paths = {
        REPO_ROOT / 'backend' / 'app' / 'app_platform',
        REPO_ROOT / 'backend' / 'tests' / 'app_platform',
        REPO_ROOT / 'backend' / 'app' / 'mcp' / 'tools' / 'app_tools.py',
    }

    remaining = [path.relative_to(REPO_ROOT).as_posix() for path in legacy_paths if path.exists()]

    assert remaining == []


def test_builtin_knowledge_manifest_matches_p0_contract() -> None:
    from backend.app.hasn.service.ai_native_builtin_manifests import KNOWLEDGE_AI_NATIVE_MANIFEST

    manifest = KNOWLEDGE_AI_NATIVE_MANIFEST

    assert manifest['app_id'] == 'knowledge'
    assert manifest['version'] == '1.0.0'
    assert manifest['workspace_scope'] == ['personal', 'enterprise']
    assert manifest['collaboration_mode'] == 'workspace_shared'
    assert manifest['capabilities'][0]['tool_id'] == 'knowledge.search'
    assert manifest['capabilities'][0]['mcp_name'] == 'hasn.knowledge.search'
    assert manifest['capabilities'][0]['required_scopes'] == ['knowledge.read']
    assert manifest['tools'][0]['handler'] == 'knowledge.search'
    assert manifest['tools'][0]['idempotent'] is True


def test_manifest_validator_accepts_builtin_knowledge_manifest() -> None:
    from backend.app.hasn.service.ai_native_app_registry import AINativeAppRegistry
    from backend.app.hasn.service.ai_native_builtin_manifests import KNOWLEDGE_AI_NATIVE_MANIFEST
    from backend.app.hasn.service.workbench_app_registry import workbench_app_registry

    registry = AINativeAppRegistry(workbench_registry=workbench_app_registry)

    result = registry.validate_manifest(KNOWLEDGE_AI_NATIVE_MANIFEST)

    assert result.valid is True
    assert result.errors == []
    assert result.manifest_hash.startswith('sha256:')


def test_manifest_validator_rejects_unknown_workbench_app() -> None:
    from backend.app.hasn.service.ai_native_app_registry import AINativeAppRegistry

    registry = AINativeAppRegistry()
    manifest = {
        'app_id': 'unknown',
        'version': '1.0.0',
        'workspace_scope': ['personal'],
        'collaboration_mode': 'none',
        'capabilities': [],
        'tools': [],
        'events': [],
        'reverse_invoke': {'supported': False},
        'audit': {'fields': ['trace_id', 'workspace', 'app_id', 'decision']},
    }

    result = registry.validate_manifest(manifest)

    assert result.valid is False
    assert 'workbench_app_not_found' in result.errors


def test_manifest_validator_rejects_scope_and_collaboration_drift() -> None:
    from backend.app.hasn.service.ai_native_app_registry import AINativeAppRegistry
    from backend.app.hasn.service.ai_native_builtin_manifests import KNOWLEDGE_AI_NATIVE_MANIFEST
    from backend.app.hasn.service.workbench_app_registry import WorkbenchApp, WorkbenchAppRegistry

    workbench = WorkbenchAppRegistry()
    workbench.register(
        WorkbenchApp(
            id='knowledge',
            name='知识库',
            icon='book-open',
            description='个人知识库',
            scope=('personal',),
            collaboration_mode='none',
            entry_route='/workbench/apps/knowledge',
            install_policy='auto',
        )
    )
    registry = AINativeAppRegistry(workbench_registry=workbench)

    result = registry.validate_manifest(KNOWLEDGE_AI_NATIVE_MANIFEST)

    assert result.valid is False
    assert 'workspace_scope_exceeds_workbench_scope' in result.errors
    assert 'collaboration_mode_mismatch' in result.errors


def test_hasn_router_mounts_ai_native_app_routes() -> None:
    from backend.app.hasn.api.router import ai_native

    routes = {route.path for route in ai_native.routes}

    assert '/api/v1/ai-native/apps' in routes
    assert '/api/v1/ai-native/apps/{app_id}' in routes
    assert '/api/v1/ai-native/apps/{app_id}/validate' in routes
    assert '/api/v1/ai-native/apps/{app_id}/publish' in routes


@pytest.mark.asyncio
async def test_publish_builtin_manifest_uses_published_status() -> None:
    from backend.app.hasn.service.ai_native_app_registry import AINativeAppRegistry
    from backend.app.hasn.service.ai_native_builtin_manifests import KNOWLEDGE_AI_NATIVE_MANIFEST
    from backend.app.hasn.service.workbench_app_registry import workbench_app_registry

    registry = AINativeAppRegistry(workbench_registry=workbench_app_registry)
    saved = await registry.publish_builtin(None, 'knowledge')

    assert saved['app_id'] == 'knowledge'
    assert saved['status'] == 'published'
    assert saved['manifest_json'] == KNOWLEDGE_AI_NATIVE_MANIFEST
    assert saved['manifest_hash'].startswith('sha256:')


class _ScalarResult:
    def __init__(self, rows: list[Any]) -> None:
        self._rows = rows

    def scalars(self) -> '_ScalarResult':
        return self

    def first(self) -> Any:
        return self._rows[0] if self._rows else None

    def all(self) -> list[Any]:
        return list(self._rows)


class _FakeDb:
    def __init__(
        self,
        *,
        workspace: dict[str, Any] | None,
        app_row: Any = None,
        audit_rows: list[Any] | None = None,
    ) -> None:
        self.workspace = workspace
        self.app_row = app_row
        self.audit_rows = list(audit_rows or [])
        self.added: list[Any] = []

    async def execute(self, stmt: Any) -> _ScalarResult:
        sql = str(stmt)
        if 'hasn_workspace_app' in sql:
            return _ScalarResult([self.app_row] if self.app_row is not None else [])
        if 'hasn_ai_native_app_audit' in sql:
            rows = list(self.audit_rows)
            params = getattr(getattr(stmt, 'compile')(), 'params', {})
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
            return _ScalarResult(rows)
        return _ScalarResult([])

    def add(self, row: Any) -> None:
        self.added.append(row)
        if getattr(row, 'id', None) is None:
            row.id = len(self.added)

    async def flush(self) -> None:
        return None

    async def refresh(self, row: Any) -> None:
        if getattr(row, 'id', None) is None:
            row.id = len(self.added)


class _FakeAgent:
    agent_hasn_id = 'a_001'
    agent_name = 'Agent'
    owner_hasn_id = 'h_001'
    owner_user_id = 12345
    scopes = ['knowledge.read']
    session_uuid = 'session-001'


def _make_runtime_test_app(fake_db: _FakeDb, monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    from backend.app.hasn.api.v1 import ai_native_app as module
    from backend.database.db import get_db, get_db_transaction

    app = FastAPI()
    app.include_router(module.runtime_router, prefix='/api/v1/ai-native/runtime')
    app.include_router(module.audit_router, prefix='/api/v1/ai-native/audit')

    async def fake_agent_auth() -> None:
        return None

    async def fake_db_session():
        yield fake_db

    async def fake_db_transaction():
        yield fake_db

    app.dependency_overrides[module.DependsAgentJwtAuth.dependency] = fake_agent_auth
    app.dependency_overrides[get_db] = fake_db_session
    app.dependency_overrides[get_db_transaction] = fake_db_transaction
    monkeypatch.setattr(module.ai_native_runtime_gateway, '_require_agent', lambda _request: _FakeAgent())
    return app


def test_runtime_capabilities_returns_current_workspace_knowledge_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.hasn.api.v1 import ai_native_app as module
    from backend.app.hasn.model import HasnWorkspaceApp
    from backend.app.hasn.service import ai_native_runtime_gateway as gateway_module

    fake_db = _FakeDb(
        workspace={'kind': 'personal', 'enterprise_id': None},
        app_row=HasnWorkspaceApp(
            workspace_kind='personal',
            user_id=12345,
            enterprise_id=None,
            app_id='knowledge',
            status='active',
            config={},
            enabled_by=12345,
        ),
    )
    app = _make_runtime_test_app(fake_db, monkeypatch)

    async def fake_active_workspace(_db: Any, *, user_id: int) -> dict[str, Any]:
        assert user_id == 12345
        return {'kind': 'personal', 'enterprise_id': None}

    monkeypatch.setattr(gateway_module.workbench_domain_service, 'get_active_workspace', fake_active_workspace)

    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/ai-native/runtime/capabilities',
            json={'workspace': None, 'include_disabled': False, 'trace_id': 'trace-1'},
            headers={'Authorization': 'Bearer test-agent'},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()['data']
    assert data['workspace'] == {
        'kind': 'personal',
        'user_id': 12345,
        'enterprise_id': None,
        'workspace_key': 'personal:12345',
    }
    assert data['tools'][0]['tool_id'] == 'knowledge.search'
    assert data['tools'][0]['mcp_name'] == 'hasn.knowledge.search'
    assert data['tools'][0]['required_scopes'] == ['knowledge.read']


def test_runtime_capabilities_filters_disabled_workspace_app(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.hasn.model import HasnWorkspaceApp
    from backend.app.hasn.service import ai_native_runtime_gateway as gateway_module

    fake_db = _FakeDb(
        workspace={'kind': 'personal', 'enterprise_id': None},
        app_row=HasnWorkspaceApp(
            workspace_kind='personal',
            user_id=12345,
            enterprise_id=None,
            app_id='knowledge',
            status='disabled',
            config={},
            enabled_by=12345,
        ),
    )
    app = _make_runtime_test_app(fake_db, monkeypatch)

    async def fake_active_workspace(_db: Any, *, user_id: int) -> dict[str, Any]:
        return {'kind': 'personal', 'enterprise_id': None}

    monkeypatch.setattr(gateway_module.workbench_domain_service, 'get_active_workspace', fake_active_workspace)

    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/ai-native/runtime/capabilities',
            json={'workspace': None, 'include_disabled': False, 'trace_id': 'trace-disabled-discovery'},
            headers={'Authorization': 'Bearer test-agent'},
        )

    assert resp.status_code == 200, resp.text
    assert resp.json()['data']['tools'] == []


def test_runtime_tool_call_invokes_real_knowledge_search_and_writes_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.hasn.api.v1 import ai_native_app as module
    from backend.app.hasn.model import HasnWorkspaceApp
    from backend.app.hasn.service import ai_native_runtime_gateway as gateway_module

    fake_db = _FakeDb(
        workspace={'kind': 'personal', 'enterprise_id': None},
        app_row=HasnWorkspaceApp(
            workspace_kind='personal',
            user_id=12345,
            enterprise_id=None,
            app_id='knowledge',
            status='active',
            config={},
            enabled_by=12345,
        ),
    )
    app = _make_runtime_test_app(fake_db, monkeypatch)

    async def fake_active_workspace(_db: Any, *, user_id: int) -> dict[str, Any]:
        assert user_id == 12345
        return {'kind': 'personal', 'enterprise_id': None}

    async def fake_search(_db: Any, *, user_id: int, query: str, limit: int, dataset_id: str | None) -> dict[str, Any]:
        assert (user_id, query, limit, dataset_id) == (12345, '唤星工作台', 10, None)
        return {'items': [{'id': 'chunk-1', 'content': query}], 'total': 1}

    monkeypatch.setattr(gateway_module.workbench_domain_service, 'get_active_workspace', fake_active_workspace)
    monkeypatch.setattr(gateway_module.workbench_domain_service, 'search_current_knowledge', fake_search)

    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/ai-native/runtime/tools/knowledge/knowledge.search/call',
            json={
                'workspace': None,
                'input': {'query': '唤星工作台', 'limit': 10, 'dataset_id': None},
                'trace_id': 'trace-2',
            },
            headers={'Authorization': 'Bearer test-agent'},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()['data']
    assert data['decision'] == 'allow'
    assert data['result']['items'] == [{'id': 'chunk-1', 'content': '唤星工作台'}]
    audit_row = fake_db.added[-1]
    assert data['audit_id'] == audit_row.id
    assert audit_row.trace_id == 'trace-2'
    assert audit_row.decision == 'allow'


def test_runtime_tool_call_scope_denial_writes_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.hasn.api.v1 import ai_native_app as module
    from backend.app.hasn.model import HasnWorkspaceApp
    from backend.app.hasn.service import ai_native_runtime_gateway as gateway_module

    class NoKnowledgeScopeAgent(_FakeAgent):
        scopes = ['message.read']

    fake_db = _FakeDb(
        workspace={'kind': 'personal', 'enterprise_id': None},
        app_row=HasnWorkspaceApp(
            workspace_kind='personal',
            user_id=12345,
            enterprise_id=None,
            app_id='knowledge',
            status='active',
            config={},
            enabled_by=12345,
        ),
    )
    app = _make_runtime_test_app(fake_db, monkeypatch)

    async def fake_active_workspace(_db: Any, *, user_id: int) -> dict[str, Any]:
        return {'kind': 'personal', 'enterprise_id': None}

    monkeypatch.setattr(module.ai_native_runtime_gateway, '_require_agent', lambda _request: NoKnowledgeScopeAgent())
    monkeypatch.setattr(gateway_module.workbench_domain_service, 'get_active_workspace', fake_active_workspace)

    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/ai-native/runtime/tools/knowledge/knowledge.search/call',
            json={'workspace': None, 'input': {'query': '唤星工作台'}, 'trace_id': 'trace-3'},
            headers={'Authorization': 'Bearer test-agent'},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()['data']
    assert data['decision'] == 'deny'
    assert data['error'] == {'code': '15012', 'message': 'agent_scope_missing'}
    audit_row = fake_db.added[-1]
    assert audit_row.decision == 'deny'
    assert audit_row.error_code == '15012'


def test_runtime_tool_call_disabled_app_writes_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.hasn.api.v1 import ai_native_app as module
    from backend.app.hasn.model import HasnWorkspaceApp
    from backend.app.hasn.service import ai_native_runtime_gateway as gateway_module

    fake_db = _FakeDb(
        workspace={'kind': 'personal', 'enterprise_id': None},
        app_row=HasnWorkspaceApp(
            workspace_kind='personal',
            user_id=12345,
            enterprise_id=None,
            app_id='knowledge',
            status='disabled',
            config={},
            enabled_by=12345,
        ),
    )
    app = _make_runtime_test_app(fake_db, monkeypatch)

    async def fake_active_workspace(_db: Any, *, user_id: int) -> dict[str, Any]:
        return {'kind': 'personal', 'enterprise_id': None}

    monkeypatch.setattr(gateway_module.workbench_domain_service, 'get_active_workspace', fake_active_workspace)

    with TestClient(app) as client:
        resp = client.post(
            '/api/v1/ai-native/runtime/tools/knowledge/knowledge.search/call',
            json={'workspace': None, 'input': {'query': '唤星工作台'}, 'trace_id': 'trace-disabled'},
            headers={'Authorization': 'Bearer test-agent'},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()['data']
    assert data['decision'] == 'deny'
    assert data['error'] == {'code': '15002', 'message': 'app_not_enabled'}
    audit_row = fake_db.added[-1]
    assert audit_row.decision == 'deny'
    assert audit_row.error_code == '15002'


def test_runtime_audit_route_applies_query_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.hasn.model import HasnAiNativeAppAudit

    matching_row = HasnAiNativeAppAudit(
        trace_id='trace-1',
        step='runtime',
        workspace_kind='personal',
        user_id=12345,
        enterprise_id=None,
        app_id='knowledge',
        app_version='1.0.0',
        actor_type='agent',
        agent_hasn_id='a_001',
        owner_hasn_id='h_001',
        session_uuid='session-001',
        method='tool_call',
        capability_id='knowledge.search.capability',
        tool_id='knowledge.search',
        event_type='tool_call',
        required_scopes=['knowledge.read'],
        agent_scopes_snapshot=['knowledge.read'],
        workspace_role='owner',
        risk_level='low',
        decision='allow',
        confirmation_id=None,
        result_ref='knowledge:knowledge.search:trace-1',
        error_code=None,
        context={},
    )
    matching_row.id = 42
    other_row = HasnAiNativeAppAudit(
        trace_id='trace-2',
        step='runtime',
        workspace_kind='enterprise',
        user_id=None,
        enterprise_id=7,
        app_id='knowledge',
        app_version='1.0.0',
        actor_type='agent',
        agent_hasn_id='a_002',
        owner_hasn_id='h_002',
        session_uuid='session-002',
        method='tool_call',
        capability_id='knowledge.search.capability',
        tool_id='knowledge.search',
        event_type='tool_call',
        required_scopes=['knowledge.read'],
        agent_scopes_snapshot=['knowledge.read'],
        workspace_role='member',
        risk_level='low',
        decision='deny',
        confirmation_id=None,
        result_ref=None,
        error_code='15012',
        context={},
    )
    other_row.id = 43
    fake_db = _FakeDb(workspace=None, audit_rows=[matching_row, other_row])
    app = _make_runtime_test_app(fake_db, monkeypatch)

    with TestClient(app) as client:
        resp = client.get(
            '/api/v1/ai-native/audit',
            params={'workspace_kind': 'personal', 'app_id': 'knowledge', 'agent_hasn_id': 'a_001'},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()['data']
    assert data['total'] == 1
    assert data['items'][0]['trace_id'] == 'trace-1'


def test_runtime_audit_route_applies_created_at_range_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.hasn.model import HasnAiNativeAppAudit

    older_row = HasnAiNativeAppAudit(
        trace_id='trace-old',
        step='runtime',
        workspace_kind='personal',
        user_id=12345,
        enterprise_id=None,
        app_id='knowledge',
        app_version='1.0.0',
        actor_type='agent',
        agent_hasn_id='a_001',
        owner_hasn_id='h_001',
        session_uuid='session-001',
        method='tool_call',
        capability_id='knowledge.search.capability',
        tool_id='knowledge.search',
        event_type='tool_call',
        required_scopes=['knowledge.read'],
        agent_scopes_snapshot=['knowledge.read'],
        workspace_role='owner',
        risk_level='low',
        decision='allow',
        confirmation_id=None,
        result_ref='knowledge:knowledge.search:trace-old',
        error_code=None,
        context={},
    )
    older_row.id = 40
    older_row.created_at = datetime(2026, 5, 19, 8, 0, tzinfo=timezone.utc)

    matching_row = HasnAiNativeAppAudit(
        trace_id='trace-in-range',
        step='runtime',
        workspace_kind='personal',
        user_id=12345,
        enterprise_id=None,
        app_id='knowledge',
        app_version='1.0.0',
        actor_type='agent',
        agent_hasn_id='a_001',
        owner_hasn_id='h_001',
        session_uuid='session-001',
        method='tool_call',
        capability_id='knowledge.search.capability',
        tool_id='knowledge.search',
        event_type='tool_call',
        required_scopes=['knowledge.read'],
        agent_scopes_snapshot=['knowledge.read'],
        workspace_role='owner',
        risk_level='low',
        decision='allow',
        confirmation_id=None,
        result_ref='knowledge:knowledge.search:trace-in-range',
        error_code=None,
        context={},
    )
    matching_row.id = 41
    matching_row.created_at = datetime(2026, 5, 20, 8, 0, tzinfo=timezone.utc)

    newer_row = HasnAiNativeAppAudit(
        trace_id='trace-new',
        step='runtime',
        workspace_kind='personal',
        user_id=12345,
        enterprise_id=None,
        app_id='knowledge',
        app_version='1.0.0',
        actor_type='agent',
        agent_hasn_id='a_001',
        owner_hasn_id='h_001',
        session_uuid='session-001',
        method='tool_call',
        capability_id='knowledge.search.capability',
        tool_id='knowledge.search',
        event_type='tool_call',
        required_scopes=['knowledge.read'],
        agent_scopes_snapshot=['knowledge.read'],
        workspace_role='owner',
        risk_level='low',
        decision='allow',
        confirmation_id=None,
        result_ref='knowledge:knowledge.search:trace-new',
        error_code=None,
        context={},
    )
    newer_row.id = 42
    newer_row.created_at = datetime(2026, 5, 21, 8, 0, tzinfo=timezone.utc)

    fake_db = _FakeDb(workspace=None, audit_rows=[older_row, matching_row, newer_row])
    app = _make_runtime_test_app(fake_db, monkeypatch)

    with TestClient(app) as client:
        resp = client.get(
            '/api/v1/ai-native/audit',
            params={
                'created_at_from': '2026-05-20T00:00:00Z',
                'created_at_to': '2026-05-20T23:59:59Z',
            },
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()['data']
    assert data['total'] == 1
    assert data['items'][0]['trace_id'] == 'trace-in-range'
