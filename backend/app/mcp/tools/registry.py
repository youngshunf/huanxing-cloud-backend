"""
工具注册表
"""

from backend.app.mcp.tools.base import BaseTool

# 云端 server 默认 bootstrap 暴露云端发现工具（03 §3）。
BOOTSTRAP_TOOL_NAMES = frozenset({"hasn.cloud.tool.search"})


class ToolRegistry:
    """工具注册表"""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        # 迁移别名：别名 → canonical 名。别名可被 get_tool 解析，但不进入
        # 列表/发现投影，保证发现保持 canonical（与 Rust ToolRegistry 对齐）。
        self._aliases: dict[str, str] = {}

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def register_alias(self, alias: str, canonical: str) -> None:
        """注册迁移别名，解析到已存在的 canonical 工具。"""
        self._aliases[alias] = canonical

    def get_tool(self, name: str) -> BaseTool | None:
        """获取工具，解析迁移别名。"""
        tool = self._tools.get(name)
        if tool is not None:
            return tool
        canonical = self._aliases.get(name)
        if canonical is not None:
            return self._tools.get(canonical)
        return None

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
