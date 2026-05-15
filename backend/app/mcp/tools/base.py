"""
MCP 工具基类
"""
from abc import ABC, abstractmethod
from typing import Any


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
        arguments: dict[str, Any],
        agent_context: 'AgentContext'
    ) -> Any:
        """执行工具"""
        pass
