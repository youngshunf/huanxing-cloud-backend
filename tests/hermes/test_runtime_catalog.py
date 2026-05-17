"""Unit tests for the §5.5 runtime selection wiring on the backend.

Verifies (a) the static runtime catalog payload shape and (b) that
`CreateAgentPayload` strictly enforces the §6 `secret://` boundary on
runtime credential references — plaintext endpoint/auth values must be
rejected before the service layer ever sees them.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.hermes.api.v1.app.agents import CreateAgentPayload
from backend.app.hermes.api.v1.app.runtime_catalog import _CATALOG


# ----------------------------------------------------------------------------
# Catalog payload
# ----------------------------------------------------------------------------


def test_catalog_lists_local_hermes_as_default() -> None:
    """PR5 keeps the catalog static; the WebUI uses it to populate the
    Runtime selector. Hermes/local is the only P0 runtime."""
    assert len(_CATALOG) == 1
    entry = _CATALOG[0]
    assert entry['type'] == 'hermes'
    assert entry['location'] == 'local'
    assert entry['default'] is True
    assert entry['capabilities']['streaming'] is True
    assert entry['capabilities']['mcp_tools'] == 'local_endpoint'
    assert 'production' in entry['capabilities']['dispatch_modes']


def test_catalog_does_not_leak_endpoints_or_credentials() -> None:
    """Per §6, endpoint/auth/tenant must live exclusively in hasn-node.
    The catalog is static metadata only — no credential surface."""
    forbidden_keys = {'endpoint', 'endpoint_ref', 'auth', 'auth_ref', 'tenant', 'tenant_ref'}
    for entry in _CATALOG:
        keys = set(entry.keys()) | set(entry.get('capabilities', {}).keys())
        leaked = keys & forbidden_keys
        assert not leaked, f'catalog must not expose credentials, leaked: {leaked}'


# ----------------------------------------------------------------------------
# CreateAgentPayload runtime fields
# ----------------------------------------------------------------------------


def test_create_payload_defaults_to_hermes_local_with_no_runtime_refs() -> None:
    payload = CreateAgentPayload(agent_name='alpha')
    assert payload.runtime_type == 'hermes'
    assert payload.runtime_location == 'local'
    assert payload.endpoint_ref is None
    assert payload.auth_ref is None
    assert payload.tenant_ref is None


def test_create_payload_accepts_well_formed_secret_refs() -> None:
    payload = CreateAgentPayload(
        agent_name='alpha',
        runtime_type='hermes',
        runtime_location='local',
        endpoint_ref='secret://runtime/hermes/local-endpoint',
        auth_ref='secret://runtime/hermes/local-hmac',
        tenant_ref='secret://runtime/hermes/local-tenant',
    )
    assert payload.endpoint_ref == 'secret://runtime/hermes/local-endpoint'
    assert payload.auth_ref == 'secret://runtime/hermes/local-hmac'
    assert payload.tenant_ref == 'secret://runtime/hermes/local-tenant'


def test_create_payload_rejects_plaintext_endpoint() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateAgentPayload(
            agent_name='alpha',
            endpoint_ref='http://localhost:8741',
        )
    assert 'secret://' in str(exc_info.value)


def test_create_payload_rejects_plaintext_auth_ref() -> None:
    with pytest.raises(ValidationError):
        CreateAgentPayload(
            agent_name='alpha',
            auth_ref='Bearer plaintext-token',
        )


def test_create_payload_rejects_unknown_runtime_type() -> None:
    with pytest.raises(ValidationError):
        CreateAgentPayload(agent_name='alpha', runtime_type='claude_code')


def test_create_payload_rejects_unknown_runtime_location() -> None:
    with pytest.raises(ValidationError):
        CreateAgentPayload(agent_name='alpha', runtime_location='edge')


def test_create_payload_legacy_callers_still_validate() -> None:
    """Legacy WebUI/API clients that don't supply runtime fields must
    keep working — the new fields are all optional with defaults."""
    payload = CreateAgentPayload(
        agent_name='legacy',
        template='assistant',
        timezone='Asia/Shanghai',
        soul='test soul',
        user_profile='test user',
        auto_start_gateway=True,
        llm_mode='platform',
    )
    assert payload.runtime_type == 'hermes'
    assert payload.runtime_location == 'local'
    assert payload.endpoint_ref is None
