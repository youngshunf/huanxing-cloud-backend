"""
HASN 云端 MCP StreamableHTTP Server

使用 MCP SDK 的 StreamableHTTP 协议暴露云端工具
"""
import logging
from typing import Any
from contextvars import ContextVar

from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp import types
from starlette.types import Receive, Scope, Send

from backend.app.mcp.auth import AgentContext
from backend.app.mcp.server import mcp_server
from backend.common.security.agent_jwt import verify_agent_token
from backend.common.exception import errors
from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.database.db import async_db_session

logger = logging.getLogger(__name__)

# 使用 ContextVar 在异步上下文中传递 AgentContext
_streamable_agent_context: ContextVar[AgentContext | None] = ContextVar(
    'streamable_agent_context',
    default=None
)


class HasnMcpStreamableServer:
    """HASN MCP StreamableHTTP Server"""

    def __init__(self):
        self.server = Server("hasn-cloud-mcp")
        self.session_manager: StreamableHTTPSessionManager | None = None

        # 注册处理器
        self._register_handlers()

    def _register_handlers(self):
        """注册 MCP 协议处理器"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """列出可用工具"""
            try:
                # 从 ContextVar 获取 AgentContext
                agent_context = _streamable_agent_context.get()
                if agent_context is None:
                    raise RuntimeError("AgentContext not found in request context")

                # 调用现有的 HasnCloudMcpServer
                tools_data = await mcp_server.list_tools(agent_context)

                # 转换为 MCP types.Tool
                tools = []
                for tool_data in tools_data:
                    tools.append(types.Tool(
                        name=tool_data["name"],
                        description=tool_data["description"],
                        inputSchema=tool_data["input_schema"]
                    ))

                logger.info(f"Listed {len(tools)} tools for agent {agent_context.hasn_id}")
                return tools

            except Exception as e:
                logger.error(f"Error listing tools: {e}", exc_info=True)
                raise

        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: dict[str, Any]
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """调用工具"""
            try:
                # 从 ContextVar 获取 AgentContext
                agent_context = _streamable_agent_context.get()
                if agent_context is None:
                    raise RuntimeError("AgentContext not found in request context")

                logger.info(f"Agent {agent_context.hasn_id} calling tool: {name}")

                # 调用现有的 HasnCloudMcpServer
                result = await mcp_server.call_tool(agent_context, name, arguments)

                # 转换为 MCP TextContent
                import json
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}", exc_info=True)
                raise

    async def _authenticate_from_headers(self, headers: dict[bytes, bytes]) -> AgentContext:
        """
        从 HTTP headers 中提取并验证 AgentContext

        Args:
            headers: ASGI headers dict

        Returns:
            AgentContext

        Raises:
            ValueError: 认证失败
        """
        # 提取 Authorization header
        auth_header = headers.get(b"authorization")
        if not auth_header:
            raise ValueError("Missing Authorization header")

        auth_str = auth_header.decode("utf-8")
        if not auth_str.startswith("Bearer "):
            raise ValueError("Invalid Authorization header format")

        token = auth_str[7:]  # 移除 "Bearer " 前缀

        # 提取 X-HASN-Agent-ID header
        agent_id_header = headers.get(b"x-hasn-agent-id")
        if not agent_id_header:
            raise ValueError("Missing X-HASN-Agent-ID header")

        hasn_id = agent_id_header.decode("utf-8")

        # 验证 Agent JWT and its revocable Redis-backed session record.
        try:
            payload = await verify_agent_token(token)
        except errors.TokenError as e:
            raise ValueError(f"Invalid token: {e}")

        # 验证 hasn_id 匹配
        if payload.agent_hasn_id != hasn_id:
            raise ValueError("Agent ID mismatch")

        # 加载 Agent 信息验证状态
        async with async_db_session() as db:
            agent = await hasn_agents_dao.get_by_hasn_id(db, hasn_id=hasn_id)

            if not agent:
                raise ValueError("Agent not found")

            if agent.status != 'active':
                raise ValueError(f"Agent is {agent.status}")

        return AgentContext.from_token_payload(payload, agent_status=agent.status)

    async def handle_request_with_auth(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """
        处理 ASGI 请求，先进行认证，然后委托给 session_manager

        Args:
            scope: ASGI scope
            receive: ASGI receive function
            send: ASGI send function
        """
        try:
            # 从 ASGI scope 中提取 headers
            headers = dict(scope.get("headers", []))

            # 认证并获取 AgentContext
            agent_context = await self._authenticate_from_headers(headers)

            # 将 AgentContext 存储到 ContextVar
            _streamable_agent_context.set(agent_context)

            logger.debug(f"Authenticated agent {agent_context.hasn_id} for MCP request")

            # 委托给 session_manager 处理实际的 MCP 请求
            if self.session_manager is None:
                raise RuntimeError("Session manager not initialized")

            await self.session_manager.handle_request(scope, receive, send)

        except Exception as e:
            logger.error(f"Authentication failed: {e}", exc_info=True)
            # 返回 401 错误
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"error": "Authentication failed"}',
            })
        finally:
            # 清理 ContextVar
            _streamable_agent_context.set(None)

    def create_session_manager(self) -> StreamableHTTPSessionManager:
        """创建 StreamableHTTP 会话管理器"""
        if self.session_manager is None:
            self.session_manager = StreamableHTTPSessionManager(
                self.server,
                stateless=True  # 使用无状态模式，每次请求创建新 transport
            )
        return self.session_manager


# 全局实例
hasn_streamable_server = HasnMcpStreamableServer()
