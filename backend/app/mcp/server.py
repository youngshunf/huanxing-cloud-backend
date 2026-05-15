"""
HASN 云端 MCP Server

提供云端工具给 Agent Runtime
"""
import logging
import json
from typing import Any

from backend.app.mcp.auth import AgentContext
from backend.app.mcp.tools.registry import ToolRegistry
from backend.app.mcp.tools.base import BaseTool
from backend.app.mcp.tools.message import MessageSendTool, MessageListTool
from backend.app.mcp.tools.contact import ContactListTool
from backend.app.mcp.tools.app_tools import load_app_tools_for_agent, load_app_tools_for_owner

logger = logging.getLogger(__name__)


class HasnCloudMcpServer:
    """HASN 云端 MCP Server"""

    def __init__(self):
        self.tool_registry = ToolRegistry()

        # 注册内置工具
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """注册内置工具"""
        # 消息工具
        self.tool_registry.register(MessageSendTool())
        self.tool_registry.register(MessageListTool())

        # 联系人工具
        self.tool_registry.register(ContactListTool())

        logger.info(f"Registered {len(self.tool_registry.get_all_tools())} builtin tools")

    async def list_tools(
        self,
        agent_context: AgentContext,
        namespace: str | None = None
    ) -> list[dict[str, Any]]:
        """
        列出可用工具

        Args:
            agent_context: Agent 上下文
            namespace: 可选的命名空间过滤

        Returns:
            工具列表
        """
        try:
            # 动态加载 App Tools
            await self._load_app_tools(agent_context)

            # 获取所有工具
            if namespace:
                tools = self.tool_registry.get_tools_by_namespace(namespace)
            else:
                tools = self.tool_registry.get_all_tools()

            # 根据 Agent 权限过滤工具
            available_tools = []
            for tool in tools:
                if self._check_tool_permission(agent_context, tool):
                    available_tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema,
                    })

            logger.info(
                f"Agent {agent_context.hasn_id} listed {len(available_tools)} tools"
            )

            return available_tools
        except Exception as e:
            logger.error(f"Error listing tools: {str(e)}", exc_info=True)
            raise

    async def call_tool(
        self,
        agent_context: AgentContext,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        调用工具

        Args:
            agent_context: Agent 上下文
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        try:
            logger.info(
                f"Agent {agent_context.hasn_id} calling tool: {tool_name}"
            )

            # 查找工具
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool not found: {tool_name}")

            # 检查权限
            if not self._check_tool_permission(agent_context, tool):
                raise PermissionError(
                    f"Missing required scopes: {', '.join(tool.required_scopes)}"
                )

            # 执行工具
            result = await tool.execute(agent_context, arguments)

            # 记录审计日志
            await self._log_tool_call(
                agent_context, tool_name, arguments, result, success=True
            )

            return result
        except Exception as e:
            logger.error(
                f"Tool {tool_name} execution failed: {str(e)}",
                exc_info=True
            )

            # 记录审计日志
            try:
                await self._log_tool_call(
                    agent_context, tool_name, arguments, None,
                    success=False, error=str(e)
                )
            except:
                pass

            raise

    def _check_tool_permission(
        self,
        agent_context: AgentContext,
        tool: BaseTool
    ) -> bool:
        """检查 Agent 是否有权限调用该工具"""
        return all(
            scope in agent_context.scopes
            for scope in tool.required_scopes
        )

    async def _load_app_tools(self, agent_context: AgentContext):
        """
        动态加载 App Tools

        根据 Agent 的安装情况，动态注册可用的 App Tools
        """
        try:
            # 加载 Agent 级别的 App Tools
            agent_tools = await load_app_tools_for_agent(
                agent_id=agent_context.hasn_id,
                owner_id=agent_context.owner_id,
            )

            # 加载 Owner 级别的 App Tools
            owner_tools = await load_app_tools_for_owner(
                owner_id=agent_context.owner_id,
            )

            # 注册所有 App Tools（去重）
            all_app_tools = agent_tools + owner_tools
            registered_count = 0

            for tool in all_app_tools:
                # 如果工具已存在，跳过（避免重复注册）
                if self.tool_registry.get_tool(tool.name):
                    continue

                try:
                    self.tool_registry.register(tool)
                    registered_count += 1
                except ValueError:
                    # 工具已注册，跳过
                    pass

            if registered_count > 0:
                logger.info(
                    f"Dynamically registered {registered_count} app tools "
                    f"for agent {agent_context.hasn_id}"
                )

        except Exception as e:
            logger.error(f"Failed to load app tools: {e}", exc_info=True)
            # 不抛出异常，允许继续使用内置工具

    async def _log_tool_call(
        self,
        agent_context: AgentContext,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
        success: bool,
        error: str | None = None
    ):
        """记录工具调用审计日志"""
        try:
            from backend.app.hasn.service.hasn_audit_log_service import HasnAuditLogService
            from backend.database.db import async_db_session

            async with async_db_session() as db:
                audit_service = HasnAuditLogService()
                await audit_service.append(
                    db=db,
                    actor_type="agent",
                    actor_id=agent_context.hasn_id,
                    action="mcp_tool_call",
                    target_type="tool",
                    target_id=tool_name,
                    details={
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "result": result if success else None,
                        "error": error,
                        "success": success
                    }
                )
        except Exception as e:
            logger.error(f"Failed to log tool call: {str(e)}")


# 全局 MCP Server 实例
mcp_server = HasnCloudMcpServer()
