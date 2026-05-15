"""MCP 端到端测试

测试 MCP Server 的完整功能：
1. JWT 认证
2. 工具列表
3. 工具调用
4. 权限控制
5. 错误处理
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

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
    app.add_middleware(
        ContextMiddleware,
        plugins=(RequestIdPlugin(),)
    )

    register_exception(app)

    # 注意：mcp_router 已经有 prefix="/mcp"，所以这里不要再加
    app.include_router(mcp_router, tags=["MCP"])
    return app


class TestMcpAuthentication:
    """测试 MCP 认证"""

    def test_missing_authorization_header(self):
        """测试缺少 Authorization header"""
        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/list",
            headers={"X-HASN-Agent-ID": "a_test_agent_001"},
        )

        assert response.status_code == 422  # Missing required header

    def test_invalid_authorization_format(self):
        """测试无效的 Authorization 格式"""
        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/list",
            headers={
                "Authorization": "InvalidFormat token123",
                "X-HASN-Agent-ID": "a_test_agent_001",
            },
        )

        assert response.status_code == 401
        # 适配自定义错误响应格式
        json_response = response.json()
        assert "msg" in json_response
        assert "Invalid authorization header" in json_response["msg"]

    def test_expired_token(self, test_agent_expired_token):
        """测试过期的 token"""
        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/list",
            headers={
                "Authorization": f"Bearer {test_agent_expired_token}",
                "X-HASN-Agent-ID": "a_test_agent_003",
            },
        )

        assert response.status_code == 401

    def test_agent_id_mismatch(self, test_agent_token):
        """测试 Agent ID 不匹配"""
        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/list",
            headers={
                "Authorization": f"Bearer {test_agent_token}",
                "X-HASN-Agent-ID": "a_wrong_agent_id",  # 与 token 中的不匹配
            },
        )

        assert response.status_code == 401
        # 适配自定义错误响应格式
        json_response = response.json()
        assert "msg" in json_response
        assert "Agent ID mismatch" in json_response["msg"]


class TestMcpToolsList:
    """测试工具列表接口"""

    @patch("backend.app.mcp.auth.HasnAgentsService")
    @patch("backend.app.mcp.auth.async_db_session")
    def test_list_tools_success(
        self, mock_db_session, mock_agent_service, test_agent_token
    ):
        """测试成功获取工具列表"""
        # Mock Agent 查询
        mock_agent = MagicMock()
        mock_agent.status = "active"
        mock_agent.hasn_id = "a_test_agent_001"

        mock_service_instance = AsyncMock()
        mock_service_instance.get_by_hasn_id = AsyncMock(return_value=mock_agent)
        mock_agent_service.return_value = mock_service_instance

        # Mock DB session
        mock_db = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_db

        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/list",
            headers={
                "Authorization": f"Bearer {test_agent_token}",
                "X-HASN-Agent-ID": "a_test_agent_001",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)

        # 验证内置工具存在
        tool_names = [tool["name"] for tool in data["tools"]]
        assert "hasn.message.send" in tool_names
        assert "hasn.message.list" in tool_names
        assert "hasn.contact.list" in tool_names

    @patch("backend.app.mcp.auth.HasnAgentsService")
    @patch("backend.app.mcp.auth.async_db_session")
    def test_list_tools_with_namespace_filter(
        self, mock_db_session, mock_agent_service, test_agent_token
    ):
        """测试按命名空间过滤工具"""
        # Mock Agent 查询
        mock_agent = MagicMock()
        mock_agent.status = "active"
        mock_agent.hasn_id = "a_test_agent_001"

        mock_service_instance = AsyncMock()
        mock_service_instance.get_by_hasn_id = AsyncMock(return_value=mock_agent)
        mock_agent_service.return_value = mock_service_instance

        # Mock DB session
        mock_db = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_db

        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/list",
            json={"namespace": "hasn.message"},
            headers={
                "Authorization": f"Bearer {test_agent_token}",
                "X-HASN-Agent-ID": "a_test_agent_001",
            },
        )

        assert response.status_code == 200
        data = response.json()
        tools = data["tools"]

        # 验证只返回 message 命名空间的工具
        for tool in tools:
            assert tool["name"].startswith("hasn.message.")

    @patch("backend.app.mcp.auth.HasnAgentsService")
    @patch("backend.app.mcp.auth.async_db_session")
    def test_list_tools_inactive_agent(
        self, mock_db_session, mock_agent_service, test_agent_token
    ):
        """测试非活跃 Agent 无法获取工具列表"""
        # Mock Agent 查询 - 状态为 inactive
        mock_agent = MagicMock()
        mock_agent.status = "inactive"
        mock_agent.hasn_id = "a_test_agent_001"

        mock_service_instance = AsyncMock()
        mock_service_instance.get_by_hasn_id = AsyncMock(return_value=mock_agent)
        mock_agent_service.return_value = mock_service_instance

        # Mock DB session
        mock_db = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_db

        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/list",
            headers={
                "Authorization": f"Bearer {test_agent_token}",
                "X-HASN-Agent-ID": "a_test_agent_001",
            },
        )

        assert response.status_code == 403
        assert "Agent is inactive" in response.json()["detail"]


class TestMcpToolsCall:
    """测试工具调用接口"""

    @patch("backend.app.mcp.tools.contact.hasn_contacts_service")
    @patch("backend.app.mcp.auth.HasnAgentsService")
    @patch("backend.app.mcp.auth.async_db_session")
    def test_call_tool_success(
        self,
        mock_db_session,
        mock_agent_service,
        mock_contacts_service,
        test_agent_token,
    ):
        """测试成功调用工具"""
        # Mock Agent 查询
        mock_agent = MagicMock()
        mock_agent.status = "active"
        mock_agent.hasn_id = "a_test_agent_001"

        mock_service_instance = AsyncMock()
        mock_service_instance.get_by_hasn_id = AsyncMock(return_value=mock_agent)
        mock_agent_service.return_value = mock_service_instance

        # Mock DB session
        mock_db = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_db

        # Mock contacts service
        mock_contacts_service.get_list = AsyncMock(
            return_value={
                "contacts": [
                    {
                        "hasn_id": "h_contact_001",
                        "name": "Test Contact",
                        "relation": "friend",
                    }
                ],
                "total": 1,
            }
        )

        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/call",
            json={
                "tool_name": "hasn.contact.list",
                "arguments": {"limit": 10, "offset": 0},
            },
            headers={
                "Authorization": f"Bearer {test_agent_token}",
                "X-HASN-Agent-ID": "a_test_agent_001",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["result"]["total"] == 1

    @patch("backend.app.mcp.auth.HasnAgentsService")
    @patch("backend.app.mcp.auth.async_db_session")
    def test_call_tool_not_found(
        self, mock_db_session, mock_agent_service, test_agent_token
    ):
        """测试调用不存在的工具"""
        # Mock Agent 查询
        mock_agent = MagicMock()
        mock_agent.status = "active"
        mock_agent.hasn_id = "a_test_agent_001"

        mock_service_instance = AsyncMock()
        mock_service_instance.get_by_hasn_id = AsyncMock(return_value=mock_agent)
        mock_agent_service.return_value = mock_service_instance

        # Mock DB session
        mock_db = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_db

        app = make_test_app()
        client = TestClient(app)

        response = client.post(
            "/mcp/tools/call",
            json={
                "tool_name": "hasn.nonexistent.tool",
                "arguments": {},
            },
            headers={
                "Authorization": f"Bearer {test_agent_token}",
                "X-HASN-Agent-ID": "a_test_agent_001",
            },
        )

        assert response.status_code == 404
        assert "Tool not found" in response.json()["detail"]

    @patch("backend.app.mcp.auth.HasnAgentsService")
    @patch("backend.app.mcp.auth.async_db_session")
    def test_call_tool_permission_denied(
        self, mock_db_session, mock_agent_service, test_agent_readonly_token
    ):
        """测试权限不足"""
        # Mock Agent 查询
        mock_agent = MagicMock()
        mock_agent.status = "active"
        mock_agent.hasn_id = "a_test_agent_002"

        mock_service_instance = AsyncMock()
        mock_service_instance.get_by_hasn_id = AsyncMock(return_value=mock_agent)
        mock_agent_service.return_value = mock_service_instance

        # Mock DB session
        mock_db = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_db

        app = make_test_app()
        client = TestClient(app)

        # 尝试调用需要写权限的工具
        response = client.post(
            "/mcp/tools/call",
            json={
                "tool_name": "hasn.message.send",
                "arguments": {
                    "to_hasn_id": "h_recipient_001",
                    "content": "Test message",
                },
            },
            headers={
                "Authorization": f"Bearer {test_agent_readonly_token}",
                "X-HASN-Agent-ID": "a_test_agent_002",
            },
        )

        assert response.status_code == 403
        assert "Missing required scopes" in response.json()["detail"]

    @patch("backend.app.mcp.auth.HasnAgentsService")
    @patch("backend.app.mcp.auth.async_db_session")
    def test_call_tool_invalid_arguments(
        self, mock_db_session, mock_agent_service, test_agent_token
    ):
        """测试无效的工具参数"""
        # Mock Agent 查询
        mock_agent = MagicMock()
        mock_agent.status = "active"
        mock_agent.hasn_id = "a_test_agent_001"

        mock_service_instance = AsyncMock()
        mock_service_instance.get_by_hasn_id = AsyncMock(return_value=mock_agent)
        mock_agent_service.return_value = mock_service_instance

        # Mock DB session
        mock_db = AsyncMock()
        mock_db_session.return_value.__aenter__.return_value = mock_db

        app = make_test_app()
        client = TestClient(app)

        # 缺少必需参数
        response = client.post(
            "/mcp/tools/call",
            json={
                "tool_name": "hasn.message.send",
                "arguments": {},  # 缺少 to_hasn_id 和 content
            },
            headers={
                "Authorization": f"Bearer {test_agent_token}",
                "X-HASN-Agent-ID": "a_test_agent_001",
            },
        )

        assert response.status_code == 400
        assert "Missing required" in response.json()["detail"]


class TestMcpToolRegistry:
    """测试工具注册表"""

    def test_tool_registration(self):
        """测试工具注册"""
        from backend.app.mcp.tools.registry import ToolRegistry
        from backend.app.mcp.tools.base import BaseTool

        class TestTool(BaseTool):
            @property
            def name(self) -> str:
                return "test.tool"

            @property
            def description(self) -> str:
                return "Test tool"

            @property
            def input_schema(self) -> dict:
                return {"type": "object", "properties": {}}

            async def execute(self, arguments: dict, agent_context):
                return {"result": "ok"}

        registry = ToolRegistry()
        tool = TestTool()
        registry.register(tool)

        assert registry.get_tool("test.tool") is not None
        assert len(registry.get_all_tools()) == 1

    def test_namespace_filtering(self):
        """测试命名空间过滤"""
        from backend.app.mcp.tools.registry import ToolRegistry
        from backend.app.mcp.tools.base import BaseTool

        class Tool1(BaseTool):
            @property
            def name(self) -> str:
                return "ns1.tool1"

            @property
            def description(self) -> str:
                return "Tool 1"

            @property
            def input_schema(self) -> dict:
                return {"type": "object"}

            async def execute(self, arguments: dict, agent_context):
                return {}

        class Tool2(BaseTool):
            @property
            def name(self) -> str:
                return "ns2.tool2"

            @property
            def description(self) -> str:
                return "Tool 2"

            @property
            def input_schema(self) -> dict:
                return {"type": "object"}

            async def execute(self, arguments: dict, agent_context):
                return {}

        registry = ToolRegistry()
        registry.register(Tool1())
        registry.register(Tool2())

        ns1_tools = registry.get_tools_by_namespace("ns1")
        assert len(ns1_tools) == 1
        assert ns1_tools[0].name == "ns1.tool1"

        ns2_tools = registry.get_tools_by_namespace("ns2")
        assert len(ns2_tools) == 1
        assert ns2_tools[0].name == "ns2.tool2"
