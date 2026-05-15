"""
工具注册表
"""
from typing import Optional

from backend.app.mcp.tools.base import BaseTool


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)

    def get_all_tools(self) -> list[BaseTool]:
        """获取所有工具"""
        return list(self._tools.values())

    def get_tools_by_namespace(self, namespace: str) -> list[BaseTool]:
        """获取指定命名空间的工具"""
        return [
            tool for tool in self._tools.values()
            if tool.name.startswith(f"{namespace}.")
        ]
