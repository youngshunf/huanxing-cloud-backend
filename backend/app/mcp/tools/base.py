"""
MCP 工具基类
"""
from abc import ABC, abstractmethod
from typing import Any

from mcp.types import Tool


class BaseTool(ABC):
    """MCP 工具基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称（使用点分隔命名空间）"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """输入参数 JSON Schema"""
        pass

    @property
    def required_scopes(self) -> list[str]:
        """所需权限范围"""
        return []

    @abstractmethod
    async def execute(
        self,
        agent_context: 'AgentContext',
        arguments: dict[str, Any]
    ) -> Any:
        """执行工具"""
        pass

    def to_mcp_tool(self) -> Tool:
        """转换为 MCP Tool 定义"""
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema
        )
