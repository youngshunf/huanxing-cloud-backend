"""MCP 功能测试 - 不依赖数据库

测试 MCP Server 的核心功能：
1. 工具注册和列表
2. 工具调用
3. 权限检查
4. 命名空间过滤
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.mcp.routes import mcp_router
from backend.common.exception.exception_handler import register_exception


def make_test_app() -> FastAPI:
    """创建测试用的 FastAPI 应用"""
    from starlette_context.middleware import ContextMiddleware
    from starlette_context.plugins import RequestIdPlugin

    app = FastAPI()

    # 添加必要的中间件
    app.add_middleware(ContextMiddleware, plugins=(RequestIdPlugin(),))

    register_exception(app)
    app.include_router(mcp_router, tags=['MCP'])
    return app


@pytest.fixture
def valid_agent_token():
    """生成有效的 Agent JWT token"""
    from datetime import datetime, timedelta, timezone

    from backend.common.security.agent_jwt import jwt_encode_agent

    token = jwt_encode_agent({
        'token_type': 'agent',
        'agent_hasn_id': 'a_test_agent_functional',
        'agent_name': 'Functional Test Agent',
        'owner_hasn_id': 'h_test_owner',
        'owner_user_id': 1001,
        'scopes': ['message:read', 'message:write', 'contact:read'],
        'session_uuid': 'test-session-functional',
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
    })

    return token


@pytest.fixture
def mock_agent():
    """Mock Agent 对象"""
    from unittest.mock import MagicMock

    agent = MagicMock()
    agent.hasn_id = 'a_test_agent_functional'
    agent.display_name = 'Functional Test Agent'
    agent.agent_name = 'functional_test_agent'
    agent.owner_id = 'h_test_owner'
    agent.status = 'active'

    return agent


class TestMcpFunctional:
    """MCP 功能测试"""

    def test_list_tools_success(self, valid_agent_token, mock_agent) -> None:
        """测试成功获取工具列表"""
        app = make_test_app()
        client = TestClient(app)

        # Mock 数据库查询
        with patch(
            'backend.app.hasn.crud.crud_hasn_agents.hasn_agents_dao.get_by_hasn_id', new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/list',
                json={},  # 空 body，namespace 可选
                headers={
                    'Authorization': f'Bearer {valid_agent_token}',
                    'X-HASN-Agent-ID': 'a_test_agent_functional',
                },
            )

            print(f'\nStatus: {response.status_code}')
            print(f'Response: {response.json()}')

            assert response.status_code == 200
            data = response.json()
            assert 'tools' in data
            assert isinstance(data['tools'], list)

            # 渐进式暴露（设计 03 §9）：tools/list 只回 bootstrap 元工具；长尾经 tool.call 调用。
            tool_names = [tool['name'] for tool in data['tools']]
            assert 'hasn.cloud.tool.search' in tool_names
            assert 'hasn.cloud.tool.call' in tool_names
            assert 'hasn.message.send' not in tool_names  # 长尾工具不进清单
            search_tool = next(t for t in data['tools'] if t['name'] == 'hasn.cloud.tool.search')
            assert search_tool['input_schema']['required'] == ['query']

            print(f'✅ Found {len(data["tools"])} tools')
            for tool in data['tools']:
                print(f'  - {tool["name"]}: {tool["description"]}')

    def test_list_tools_ignores_namespace_filter(self, valid_agent_token, mock_agent) -> None:
        """namespace 参数被忽略，tools/list 始终返回 bootstrap 元工具集（03 §9）"""
        app = make_test_app()
        client = TestClient(app)

        with patch('backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/list',
                json={'namespace': 'hasn.message'},
                headers={
                    'Authorization': f'Bearer {valid_agent_token}',
                    'X-HASN-Agent-ID': 'a_test_agent_functional',
                },
            )

            print(f'\nStatus: {response.status_code}')
            print(f'Response: {response.json()}')

            assert response.status_code == 200
            data = response.json()
            tools = data['tools']

            # 渐进式暴露（设计 03 §9）：namespace 不收窄；始终返回 bootstrap 元工具集（不含长尾）。
            tool_names = [tool['name'] for tool in tools]
            assert 'hasn.cloud.tool.search' in tool_names
            assert 'hasn.cloud.tool.call' in tool_names
            assert 'hasn.contact.list' not in tool_names

            print(f'✅ Found {len(tools)} bootstrap tools')

    def test_call_tool_success(self, valid_agent_token, mock_agent) -> None:
        """测试成功调用工具"""
        app = make_test_app()
        client = TestClient(app)

        # contact.list 走 hasn_contacts_dao.list_contacts + _resolve_peer（DAO 真实查询，零 service 层）。
        from unittest.mock import MagicMock

        def _row(peer_id: str, peer_type: str) -> MagicMock:
            row = MagicMock()
            row.peer_id = peer_id
            row.peer_type = peer_type
            row.relation_type = 'friend'
            row.trust_level = 2
            row.status = 'connected'
            return row

        with (
            patch(
                'backend.app.hasn.crud.crud_hasn_agents.hasn_agents_dao.get_by_hasn_id', new_callable=AsyncMock
            ) as mock_get,
            patch('backend.app.mcp.tools.contact.async_db_session') as mock_contact_db_session,
            patch(
                'backend.app.mcp.tools.contact.hasn_contacts_dao.list_contacts', new_callable=AsyncMock
            ) as mock_list_contacts,
            patch('backend.app.mcp.tools.contact._resolve_peer', new_callable=AsyncMock) as mock_resolve_peer,
        ):
            mock_get.return_value = mock_agent
            mock_contact_db_session.return_value.__aenter__.return_value = MagicMock()
            mock_list_contacts.return_value = [_row('h_contact_1', 'human'), _row('a_contact_2', 'agent')]
            mock_resolve_peer.return_value = ('联系人', 'HX')

            response = client.post(
                '/mcp/tools/call',
                json={
                    'tool_name': 'hasn.contact.list',
                    'arguments': {'limit': 10},
                },
                headers={
                    'Authorization': f'Bearer {valid_agent_token}',
                    'X-HASN-Agent-ID': 'a_test_agent_functional',
                },
            )

            print(f'\nStatus: {response.status_code}')
            print(f'Response: {response.json()}')

            assert response.status_code == 200
            data = response.json()
            assert 'result' in data
            result = data['result']
            assert 'contacts' in result
            assert len(result['contacts']) == 2
            print('✅ Tool executed successfully')

    def test_call_nonexistent_tool(self, valid_agent_token, mock_agent) -> None:
        """测试调用不存在的工具"""
        app = make_test_app()
        client = TestClient(app)

        with patch('backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/call',
                json={
                    'tool_name': 'hasn.nonexistent.tool',
                    'arguments': {},
                },
                headers={
                    'Authorization': f'Bearer {valid_agent_token}',
                    'X-HASN-Agent-ID': 'a_test_agent_functional',
                },
            )

            print(f'\nStatus: {response.status_code}')
            print(f'Response: {response.json()}')

            assert response.status_code == 404  # 工具不存在返回 404
            print('✅ Correctly rejected nonexistent tool')

    def test_inactive_agent_rejected(self, valid_agent_token) -> None:
        """测试非活跃 Agent 被拒绝"""
        app = make_test_app()
        client = TestClient(app)

        # Mock 一个 inactive 的 Agent
        from unittest.mock import MagicMock

        inactive_agent = MagicMock()
        inactive_agent.hasn_id = 'a_test_agent_functional'
        inactive_agent.status = 'inactive'

        with patch('backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = inactive_agent

            response = client.post(
                '/mcp/tools/list',
                json={},  # 空 body，namespace 可选
                headers={
                    'Authorization': f'Bearer {valid_agent_token}',
                    'X-HASN-Agent-ID': 'a_test_agent_functional',
                },
            )

            print(f'\nStatus: {response.status_code}')
            print(f'Response: {response.json()}')

            assert response.status_code == 403
            data = response.json()
            assert 'inactive' in data.get('msg', '').lower() or 'inactive' in data.get('detail', '').lower()
            print('✅ Correctly rejected inactive agent')

    def test_missing_authorization(self) -> None:
        """测试缺少认证头"""
        app = make_test_app()
        client = TestClient(app)

        response = client.post('/mcp/tools/list')

        print(f'\nStatus: {response.status_code}')
        print(f'Response: {response.json()}')

        # 422 表示缺少必需参数（FastAPI 验证）
        assert response.status_code == 422
        print('✅ Correctly rejected missing authorization')

    def test_permission_check(self, valid_agent_token, mock_agent) -> None:
        """测试三态可见性（D1/D3 新模型）：默认全开；owner 把某能力设 deny 后该工具不可见。"""
        from unittest.mock import AsyncMock

        app = make_test_app()
        client = TestClient(app)

        # owner 按工具名把 hasn.message.send 与 hasn.contact.list 设 deny → 从发现里消失；
        # message.list（message:read，默认 allow）→ 仍可见。按工具名 deny 不依赖 P4 的 scope 重命名。
        deny_policy = {
            'scopes': [],
            'post_needs_review': False,
            'default_mode': 'allow',
            'capability_modes': {'hasn.message.send': 'deny', 'hasn.contact.list': 'deny'},
        }

        with (
            patch('backend.app.mcp.auth.hasn_agents_dao.get_by_hasn_id', new_callable=AsyncMock) as mock_get,
            patch('backend.app.mcp.auth.get_agent_scopes_cached', new=AsyncMock(return_value=deny_policy)),
        ):
            mock_get.return_value = mock_agent

            response = client.post(
                '/mcp/tools/call',
                json={
                    'tool_name': 'hasn.tool.search',
                    'arguments': {
                        'query': 'message',
                        'detail': 'summary',
                    },
                },
                headers={
                    'Authorization': f'Bearer {valid_agent_token}',
                    'X-HASN-Agent-ID': 'a_test_agent_functional',
                },
            )

            assert response.status_code == 200
            result = response.json()['result']
            tool_names = [tool['name'] for tool in result['tools']]

            assert 'hasn.message.list' in tool_names  # message:read 默认 allow → 可见
            assert 'hasn.message.send' not in tool_names  # message:send deny → 不可见
