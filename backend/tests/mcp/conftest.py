"""MCP 测试 fixtures"""
from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone

from backend.common.security.agent_jwt import jwt_decode_agent
from backend.common.security.agent_jwt import jwt_encode_agent


@pytest.fixture(autouse=True)
def mcp_agent_token_session(monkeypatch):
    """MCP route tests use signed Agent JWTs without a live Redis token store."""

    async def verify_test_agent_token(token: str):
        return jwt_decode_agent(token)

    monkeypatch.setattr(
        "backend.app.mcp.auth.verify_agent_token",
        verify_test_agent_token,
        raising=False,
    )


@pytest.fixture
def test_agent_token() -> str:
    """生成测试用的 Agent JWT token"""
    payload = {
        "token_type": "agent",
        "agent_hasn_id": "a_test_agent_001",
        "agent_name": "Test Agent",
        "owner_hasn_id": "h_test_owner_001",
        "owner_user_id": 1001,
        "scopes": [
            "community:read",
            "community:write",
            "message:read",
            "message:write",
            "contact:read",
            "task:execute",
            "knowledge:read",
        ],
        "session_uuid": "test-session-uuid-001",
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    return jwt_encode_agent(payload)


@pytest.fixture
def test_agent_readonly_token() -> str:
    """生成只读权限的测试 Agent JWT token"""
    payload = {
        "token_type": "agent",
        "agent_hasn_id": "a_test_agent_002",
        "agent_name": "Test Agent Readonly",
        "owner_hasn_id": "h_test_owner_001",
        "owner_user_id": 1001,
        "scopes": [
            "community:read",
            "message:read",
            "contact:read",
        ],
        "session_uuid": "test-session-uuid-002",
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    }
    return jwt_encode_agent(payload)


@pytest.fixture
def test_agent_expired_token() -> str:
    """生成已过期的测试 Agent JWT token"""
    payload = {
        "token_type": "agent",
        "agent_hasn_id": "a_test_agent_003",
        "agent_name": "Test Agent Expired",
        "owner_hasn_id": "h_test_owner_001",
        "owner_user_id": 1001,
        "scopes": ["community:read"],
        "session_uuid": "test-session-uuid-003",
        "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),  # 已过期
    }
    return jwt_encode_agent(payload)
