"""Platform MCP tool discovery."""
from __future__ import annotations

from typing import Any

from backend.app.mcp.auth import AgentContext
from backend.app.mcp.tool_directory import ToolDirectoryService, ToolSearchQuery
from backend.app.mcp.tools.base import BaseTool


class ToolSearchTool(BaseTool):
    """Search visible MCP tool sources, summaries, and schemas."""

    def __init__(self, directory: ToolDirectoryService):
        self._directory = directory

    @property
    def name(self) -> str:
        return "hasn.tool.search"

    @property
    def description(self) -> str:
        return "发现当前 Agent 可用的 MCP 工具来源、摘要和 schema"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "sources、platform、apps、app.crm、tool:hasn.crm.lead.create、crm lead create",
                },
                "source": {
                    "type": "string",
                    "enum": ["all", "platform", "app", "external", "local"],
                    "default": "all",
                },
                "detail": {
                    "type": "string",
                    "enum": ["sources", "summary", "schema"],
                    "default": "summary",
                },
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 20,
                },
                "cursor": {"type": "string"},
            },
            "required": ["query"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        agent_context: AgentContext,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        query = ToolSearchQuery(
            query=str(arguments["query"]),
            source=str(arguments.get("source", "all")),
            detail=str(arguments.get("detail", "summary")),
            page_size=int(arguments.get("page_size", 20)),
            cursor=arguments.get("cursor"),
        )
        return await self._directory.search(agent_context, query)
