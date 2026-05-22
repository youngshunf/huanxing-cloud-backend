"""Compatibility AppTool surface for MCP tests and external extensions."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.app.mcp.tools.base import BaseTool

if TYPE_CHECKING:
    from backend.app.mcp.auth import AgentContext


class AppTool(BaseTool):
    def __init__(
        self,
        installation_id: str,
        app_id: str,
        app_namespace: str,
        tool_id: str,
        tool_name: str,
        tool_description: str,
        tool_input_schema: dict[str, Any],
        tool_required_scopes: list[str],
        action: str | None = None,
        tool_output_schema: dict[str, Any] | None = None,
        risk_level: str = "low",
    ) -> None:
        self.installation_id = installation_id
        self.app_id = app_id
        self.app_namespace = app_namespace
        self.tool_id = tool_id
        self.tool_name = tool_name
        self.action = action or tool_name
        self._description = tool_description
        self._input_schema = tool_input_schema
        self._output_schema = tool_output_schema or {"type": "object"}
        self._required_scopes = tool_required_scopes
        self._risk_level = risk_level

    @property
    def source(self) -> str:
        return "app"

    @property
    def namespace(self) -> str:
        return f"hasn.{self.app_namespace}"

    @property
    def name(self) -> str:
        return f"hasn.{self.app_namespace}.{self.action}"

    @property
    def description(self) -> str:
        return self._description

    @property
    def input_schema(self) -> dict[str, Any]:
        return self._input_schema

    @property
    def output_schema(self) -> dict[str, Any]:
        return self._output_schema

    @property
    def required_scopes(self) -> list[str]:
        return self._required_scopes

    @property
    def risk_level(self) -> str:
        return self._risk_level

    async def execute(
        self,
        arguments: dict[str, Any],
        agent_context: AgentContext,
    ) -> Any:
        from backend.app.hasn.schema.ai_native_runtime import AiNativeToolCallRequest
        from backend.app.hasn.service.ai_native_runtime_gateway import ai_native_runtime_gateway
        from backend.database.db import async_db_session

        class _Request:
            state = type("_State", (), {"agent": agent_context})()

        async with async_db_session() as db:
            return await ai_native_runtime_gateway.call_tool(
                db,
                request=_Request(),
                app_id=self.app_id,
                tool_id=self.tool_id,
                body=AiNativeToolCallRequest(
                    agent_hasn_id=agent_context.hasn_id,
                    workspace={"kind": "personal"},
                    input=arguments,
                    trace_id=None,
                ),
            )
