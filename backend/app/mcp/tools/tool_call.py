"""通用调用元工具 `hasn.cloud.tool.call`（设计 03 §9）。

function-calling Runtime 只能发起 `tools/list` 中的工具调用。为在不全量暴露
（恢复 03 §1 渐进式）的前提下兑现 §7「直接调用任意 canonical name」，bootstrap
清单放一个通用调用元工具，由它把调用转发给任意已注册工具。

权限/审计/维度② 一律落**内层**工具（委托回 server.call_tool 走统一调用管线，
设计 04）；本元工具自身透明。参数 schema 校验失败时回吐内层完整 schema
（schema-on-error，见 §9.4），由 P3 实现。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from jsonschema import Draft202012Validator

from backend.app.mcp.canonical import schema_hash
from backend.app.mcp.errors import McpErrorCode, McpToolError
from backend.app.mcp.tools.base import BaseTool

if TYPE_CHECKING:
    from backend.app.mcp.auth import AgentContext
    from backend.app.mcp.server import HasnCloudMcpServer

# 不可被 tool.call 转发的元工具（防自循环 + 语义无意义）。
_NON_DISPATCHABLE = frozenset({
    "hasn.cloud.tool.call",
    "hasn.local.tool.call",
    "hasn.cloud.tool.search",
    "hasn.local.tool.search",
    "hasn.tool.search",
})


class ToolCallTool(BaseTool):
    """把调用转发给任意 canonical 工具的通用调用元工具。"""

    def __init__(self, server: HasnCloudMcpServer) -> None:
        self._server = server

    @property
    def source(self) -> str:
        return "platform"

    @property
    def name(self) -> str:
        return "hasn.cloud.tool.call"

    @property
    def description(self) -> str:
        return (
            "调用任意云端 MCP 工具：tool.call(name, params)。已知 canonical name 可直接调用，"
            "无需先 tool.search；参数错误会返回该工具的完整 schema 供修正后重试。"
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "目标工具 canonical name，如 hasn.community.create_post",
                },
                "params": {
                    "type": "object",
                    "description": "目标工具的入参",
                    "default": {},
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        }

    async def execute(
        self,
        agent_context: AgentContext,
        arguments: dict[str, Any],
    ) -> Any:
        name = str(arguments.get("name") or "").strip()
        if not name:
            raise McpToolError(McpErrorCode.TOOL_NOT_FOUND, "tool.call: missing 'name'")

        params = arguments.get("params")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise McpToolError(McpErrorCode.TOOL_NOT_FOUND, "tool.call: 'params' must be an object")

        if name in _NON_DISPATCHABLE or name == self.name:
            raise McpToolError(McpErrorCode.DIRECT_CALL_DENIED, f"tool.call cannot dispatch meta tool: {name}")

        # 解析内层工具（含迁移别名）。App 工具已由外层 call_tool 的 _load_app_tools 载入。
        inner_tool = self._server.tool_registry.get_tool(name)
        if inner_tool is None:
            raise McpToolError(McpErrorCode.TOOL_NOT_FOUND, f"Tool not found: {name}")

        # schema-on-error（§9.4）：仅参数 schema 校验失败时回吐内层完整 schema 供修正；
        # 业务失败（维度② 不可达、额度等）由内层工具透传，不附 schema。
        validation_error = self._validate_params(inner_tool, params)
        if validation_error is not None:
            return validation_error

        # 委托统一调用管线：维度① 三态闸门 + 维度② + 审计全落内层。
        return await self._server.call_tool(agent_context, name, params)

    def _validate_params(self, inner_tool: BaseTool, params: dict[str, Any]) -> dict[str, Any] | None:
        """用内层工具 input_schema 校验 params；通过返回 None，失败返回 schema-on-error 信封。"""
        schema = inner_tool.input_schema or {}
        errors = sorted(
            Draft202012Validator(schema).iter_errors(params),
            key=lambda e: [str(p) for p in e.path],
        )
        if not errors:
            return None

        missing: list[str] = []
        invalid: dict[str, str] = {}
        for error in errors:
            path = ".".join(str(p) for p in error.path)
            if error.validator == "required":
                prop = error.message.split("'")[1] if "'" in error.message else error.message
                key = f"{path}.{prop}" if path else prop
                if key not in missing:
                    missing.append(key)
            else:
                invalid.setdefault(path or "(root)", error.message)

        return {
            "ok": False,
            "error": "input_validation_failed",
            "tool": inner_tool.name,
            "missing": missing,
            "invalid": invalid,
            "input_schema": schema,
            "schema_hash": schema_hash(schema),
        }
