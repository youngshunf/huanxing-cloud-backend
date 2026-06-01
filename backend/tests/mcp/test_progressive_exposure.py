"""MCP progressive exposure contract tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.mcp.routes import mcp_router
from backend.app.mcp.tools.app_tools import AppTool
from backend.common.exception.exception_handler import register_exception
from backend.common.security.agent_jwt import jwt_encode_agent


class JsonResponse(Protocol):
    def json(self) -> dict: ...


def make_test_app() -> FastAPI:
    from starlette_context.middleware import ContextMiddleware
    from starlette_context.plugins import RequestIdPlugin

    app = FastAPI()
    app.add_middleware(ContextMiddleware, plugins=(RequestIdPlugin(),))
    register_exception(app)
    app.include_router(mcp_router, tags=['MCP'])
    return app


@pytest.fixture
def valid_agent_token() -> str:
    return jwt_encode_agent({
        'token_type': 'agent',
        'agent_hasn_id': 'a_test_agent_progressive',
        'agent_name': 'Progressive Test Agent',
        'owner_hasn_id': 'h_test_owner',
        'owner_user_id': 1001,
        'scopes': ['message:read', 'message:write', 'contact:read'],
        'session_uuid': 'test-session-progressive',
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    })


@pytest.fixture
def readonly_agent_token() -> str:
    return jwt_encode_agent({
        'token_type': 'agent',
        'agent_hasn_id': 'a_test_agent_progressive',
        'agent_name': 'Progressive Test Agent',
        'owner_hasn_id': 'h_test_owner',
        'owner_user_id': 1001,
        'scopes': ['message:read'],
        'session_uuid': 'test-session-progressive-readonly',
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    })


@pytest.fixture
def mock_agent() -> MagicMock:
    agent = MagicMock()
    agent.hasn_id = 'a_test_agent_progressive'
    agent.display_name = 'Progressive Test Agent'
    agent.agent_name = 'progressive_test_agent'
    agent.owner_id = 'h_test_owner'
    agent.status = 'active'
    return agent


def auth_headers(token: str) -> dict[str, str]:
    return {
        'Authorization': f'Bearer {token}',
        'X-HASN-Agent-ID': 'a_test_agent_progressive',
    }


def error_message(response: JsonResponse) -> str:
    data = response.json()
    return data.get('detail') or data.get('msg') or ''


class TestMcpProgressiveExposure:
    def test_source_index_keeps_platform_tools_out_of_app_namespace(
        self,
        valid_agent_token: str,
        mock_agent: MagicMock,
    ) -> None:
        app = make_test_app()
        client = TestClient(app)

        app_tool = AppTool(
            installation_id='appi_sample',
            app_id='sample',
            app_namespace='sample',
            tool_id='sample.search',
            tool_name='search',
            action='search',
            tool_description='Search workspace sample data',
            tool_input_schema={'type': 'object'},
            tool_output_schema={'type': 'object'},
            tool_required_scopes=[],
        )

        with (
            patch(
                'backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id',
                new_callable=AsyncMock,
            ) as mock_get,
            patch(
                'backend.app.mcp.server.load_app_tools_for_agent',
                new_callable=AsyncMock,
            ) as mock_load_tools,
            patch(
                'backend.app.mcp.server.load_app_tools_for_owner',
                new_callable=AsyncMock,
            ) as mock_load_owner_tools,
            patch(
                'backend.app.mcp.server.HasnCloudMcpServer._log_tool_call',
                new_callable=AsyncMock,
            ),
        ):
            mock_get.return_value = mock_agent
            mock_load_tools.return_value = [app_tool]
            mock_load_owner_tools.return_value = []

            response = client.post(
                '/mcp/tools/call',
                json={
                    'tool_name': 'hasn.tool.search',
                    'arguments': {'query': 'sources'},
                },
                headers=auth_headers(valid_agent_token),
            )

        assert response.status_code == 200
        sources = {(item['source'], item['namespace']) for item in response.json()['result']['sources']}
        assert ('app', 'hasn.sample') in sources
        assert ('platform', 'hasn.contact') in sources
        assert ('platform', 'hasn.message') in sources

    def test_list_tools_defaults_to_bootstrap_search_only(
        self,
        valid_agent_token: str,
        mock_agent: MagicMock,
    ) -> None:
        app = make_test_app()
        client = TestClient(app)

        with patch(
            'backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id',
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/list',
                json={},
                headers=auth_headers(valid_agent_token),
            )

        assert response.status_code == 200
        tool_names = [tool['name'] for tool in response.json()['tools']]
        assert tool_names == ['hasn.cloud.tool.search']

    def test_tool_search_returns_builtin_schema(
        self,
        valid_agent_token: str,
        mock_agent: MagicMock,
    ) -> None:
        app = make_test_app()
        client = TestClient(app)

        with patch(
            'backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id',
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/call',
                json={
                    'tool_name': 'hasn.tool.search',
                    'arguments': {
                        'query': 'tool:hasn.contact.list',
                        'detail': 'schema',
                    },
                },
                headers=auth_headers(valid_agent_token),
            )

        assert response.status_code == 200
        result = response.json()['result']
        assert result['query'] == 'tool:hasn.contact.list'
        assert result['tools'] == []
        assert result['schemas'][0]['name'] == 'hasn.contact.list'
        assert result['schemas'][0]['input_schema']['type'] == 'object'
        assert result['schemas'][0]['required_scopes'] == ['contact:read']

    def test_direct_call_does_not_require_prior_exposure(
        self,
        valid_agent_token: str,
        mock_agent: MagicMock,
    ) -> None:
        app = make_test_app()
        client = TestClient(app)

        mock_contact_service = MagicMock()
        mock_contact_service.get_list = AsyncMock(
            return_value={
                'data': [
                    MagicMock(
                        id=1,
                        contact_id='h_contact_1',
                        status='active',
                        created_at='2026-05-20',
                    )
                ]
            }
        )

        with (
            patch(
                'backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id',
                new_callable=AsyncMock,
            ) as mock_get,
            patch(
                'backend.app.mcp.tools.contact.HasnContactsService',
                return_value=mock_contact_service,
            ),
        ):
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/call',
                json={
                    'tool_name': 'hasn.contact.list',
                    'arguments': {'limit': 10},
                },
                headers=auth_headers(valid_agent_token),
            )

        assert response.status_code == 200
        assert response.json()['result']['contacts'][0]['contact_hasn_id'] == 'h_contact_1'

    def test_direct_call_deny_mode_is_authorization_not_exposure_failure(
        self,
        valid_agent_token: str,
        mock_agent: MagicMock,
    ) -> None:
        # 新模型（D1/D3）：默认全开，owner 把某能力设 deny 才拒。deny 是「授权拒绝」(403)，
        # 不是「未暴露/未发现」失败——区分二者仍是本用例的契约。
        app = make_test_app()
        client = TestClient(app)

        deny_policy = {
            'scopes': [],
            'post_needs_review': False,
            'default_mode': 'allow',
            'capability_modes': {'contact:read': 'deny'},
        }

        with (
            patch(
                'backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id',
                new_callable=AsyncMock,
            ) as mock_get,
            patch(
                'backend.app.mcp.auth.get_agent_scopes_cached',
                new=AsyncMock(return_value=deny_policy),
            ),
        ):
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/call',
                json={
                    'tool_name': 'hasn.contact.list',
                    'arguments': {'limit': 10},
                },
                headers=auth_headers(valid_agent_token),
            )

        assert response.status_code == 403
        message = error_message(response)
        assert 'denied' in message.lower()
        assert 'not exposed' not in message.lower()
