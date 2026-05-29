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

    def descriptor(self) -> dict[str, Any]:
        """结构化描述符投影（P0），与 Rust ToolDescriptor 对齐。

        统一暴露 source/namespace/action/schema_hash/scopes/risk/visibility/
        execution_location，供 source 维度索引与后续阶段消费。execution_location
        为 P0 占位（local 来源→local，其余→cloud），P3 由工具显式声明覆盖。
        """
        from backend.app.mcp.canonical import schema_hash, validate_canonical_name

        parsed = validate_canonical_name(self.name, self.source)
        output_schema = getattr(self, "output_schema", None)
        default_location = "local" if self.source == "local" else "cloud"
        return {
            "canonical_name": parsed.full,
            "source": self.source,
            "namespace": parsed.namespace,
            "action": parsed.action,
            "input_schema_hash": schema_hash(self.input_schema),
            "output_schema_hash": schema_hash(output_schema) if output_schema else None,
            "required_scopes": self.required_scopes,
            "risk_level": getattr(self, "risk_level", "low"),
            "schema_visibility": getattr(self, "schema_visibility", "public"),
            "execution_location": getattr(self, "execution_location", default_location),
        }

    @abstractmethod
    async def execute(
        self,
        agent_context: AgentContext,
        arguments: dict[str, Any],
    ) -> Any:
        """执行工具"""
