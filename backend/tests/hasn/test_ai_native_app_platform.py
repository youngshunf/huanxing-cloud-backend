from __future__ import annotations

from pathlib import Path

import pytest


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
        REPO_ROOT / 'backend' / 'app' / 'hasn' / 'service' / 'ai_native_audit_service.py',
    }

    missing = [path.relative_to(REPO_ROOT).as_posix() for path in expected if not path.exists()]

    assert missing == []


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
