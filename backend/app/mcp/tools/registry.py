"""
工具注册表
"""
from typing import Optional

from backend.app.mcp.tools.base import BaseTool


BOOTSTRAP_TOOL_NAMES = frozenset({"hasn.tool.search"})


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

    def list_bootstrap_tools(self) -> list[BaseTool]:
        """获取默认暴露给 Runtime 的 bootstrap 工具"""
        return [
            tool
            for name, tool in sorted(self._tools.items())
            if name in BOOTSTRAP_TOOL_NAMES
        ]

    def get_tools_by_namespace(self, namespace: str) -> list[BaseTool]:
        """获取指定命名空间的工具"""
        return [
            tool for tool in self._tools.values()
            if tool.name.startswith(f"{namespace}.")
        ]
