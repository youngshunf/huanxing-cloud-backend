"""
MCP 工具基类
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.app.mcp.auth import AgentContext


class BaseTool(ABC):
    """MCP 工具基类"""

    @property
    def source(self) -> str:
        """工具来源类别，默认平台工具。"""
        return "platform"

    @property
    def namespace(self) -> str:
        """工具命名空间，默认取 canonical 名称前两段。"""
        parts = self.name.split(".")
        if self.source == "external" and len(parts) >= 3:
            return ".".join(parts[:3])
        if len(parts) >= 2:
            return ".".join(parts[:2])
        return self.name

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称（使用点分隔命名空间）"""

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """输入参数 JSON Schema"""

    @property
    def required_scopes(self) -> list[str]:
        """所需权限范围"""
        return []

    @abstractmethod
    async def execute(
        self,
        arguments: dict[str, Any],
        agent_context: AgentContext,
    ) -> Any:
        """执行工具"""
