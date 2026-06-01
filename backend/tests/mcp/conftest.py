"""MCP 测试 fixtures"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.common.security.agent_jwt import jwt_decode_agent, jwt_encode_agent


def _allow_policy() -> dict:
    """默认全开三态策略（default_mode='allow'），与新建 Agent 一致（P2/P3 默认）。"""
    return {
        'scopes': [],
        'post_needs_review': False,
        'default_mode': 'allow',
        'capability_modes': {},
    }


@pytest.fixture(autouse=True)
def mcp_agent_token_session(monkeypatch) -> None:
    """MCP route tests use signed Agent JWTs without a live Redis token store.

    并默认 stub get_agent_scopes_cached 返回「全开」三态策略（D3 活取的 DB 现查），
    使路由/streamable 测试无需活体 DB；需要 deny/ask 的测试在用例内 override。
    """

    async def verify_test_agent_token(token: str):
        return jwt_decode_agent(token)

    async def _stub_scopes_cached(agent_hasn_id: str, db: object) -> dict:
        return _allow_policy()

    monkeypatch.setattr(
        'backend.app.mcp.auth.verify_agent_token',
        verify_test_agent_token,
        raising=False,
    )
    # 路由路径（get_agent_context）的 D3 活取走 auth 命名空间，按名 patch 为全开默认。
    # streamable 命名空间不在此 patch（其导入在 pytest 下会被本地 backend.app.mcp 包遮蔽
    # site-packages 的 mcp.server；streamable 活取链路由 E2E 真实栈覆盖）。
    monkeypatch.setattr(
        'backend.app.mcp.auth.get_agent_scopes_cached',
        _stub_scopes_cached,
        raising=False,
    )


@pytest.fixture
def test_agent_token() -> str:
    """生成测试用的 Agent JWT token"""
    payload = {
        'token_type': 'agent',
        'agent_hasn_id': 'a_test_agent_001',
        'agent_name': 'Test Agent',
        'owner_hasn_id': 'h_test_owner_001',
        'owner_user_id': 1001,
        'scopes': [
            'community:read',
            'community:write',
            'message:read',
            'message:write',
            'contact:read',
            'task:execute',
            'knowledge:read',
        ],
        'session_uuid': 'test-session-uuid-001',
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    return jwt_encode_agent(payload)


@pytest.fixture
def test_agent_readonly_token() -> str:
    """生成只读权限的测试 Agent JWT token"""
    payload = {
        'token_type': 'agent',
        'agent_hasn_id': 'a_test_agent_002',
        'agent_name': 'Test Agent Readonly',
        'owner_hasn_id': 'h_test_owner_001',
        'owner_user_id': 1001,
        'scopes': [
            'community:read',
            'message:read',
            'contact:read',
        ],
        'session_uuid': 'test-session-uuid-002',
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    return jwt_encode_agent(payload)


@pytest.fixture
def test_agent_expired_token() -> str:
    """生成已过期的测试 Agent JWT token"""
    payload = {
        'token_type': 'agent',
        'agent_hasn_id': 'a_test_agent_003',
        'agent_name': 'Test Agent Expired',
        'owner_hasn_id': 'h_test_owner_001',
        'owner_user_id': 1001,
        'scopes': ['community:read'],
        'session_uuid': 'test-session-uuid-003',
        'exp': int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),  # 已过期
    }
    return jwt_encode_agent(payload)
