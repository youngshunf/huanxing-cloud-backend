"""Agent 能力授权统一判定服务（维度①，D1/D3）。

设计事实源：13-doc《Agent 权限模型与工具目录》§3.1；实施记录见
docs/hasn-node设计文档/MCP统一工具体系/实施/94-Agent云端MCP工具调用三层修复.md。

**唯一判定入口**：所有调用面（MCP server、AI-Native Runtime 网关、将来第三方 MCP）
对「给定 agent + tool → allow/ask/deny」的判定都走本服务，不再各自 `get_agent_scopes_cached`
+ `resolve_tool_mode` 重写一遍。kernel 仍是 `scope_policy.resolve_tool_mode`（纯函数）。

两个维度只管①：能力授权（owner→agent 三态，默认全 allow，统一适用所有工具）。
维度②（对象可达性，能否给某人发消息）依赖目标/关系/信任，留在各工具 `execute` 内
（如 `message_router.check_relation_permission`），不进本服务。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.common.security.scope_policy import resolve_tool_mode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class CapabilityGuard:
    """维度① 能力授权的唯一判定服务。返回三态 mode：'allow' | 'ask' | 'deny'。"""

    async def decide(
        self,
        db: AsyncSession,
        *,
        agent_hasn_id: str,
        tool_name: str,
        required_scopes: Sequence[str] | None,
    ) -> str:
        """D3 活取：现查 `hasn_agent_scopes` 策略 + 聚合判定。

        给**手里没有预取策略**的调用面用（AI-Native Runtime 网关、将来 external）。
        快照（key/JWT scopes）仅审计、不作判定依据，故不受词表点/冒号差异影响。
        """
        # 延迟 import：让消费方对 agent_jwt.get_agent_scopes_cached 的 monkeypatch（源模块）生效。
        from backend.common.security.agent_jwt import get_agent_scopes_cached

        policy = await get_agent_scopes_cached(agent_hasn_id, db)
        return self.resolve_from_policy(
            policy.get('default_mode', 'allow'),
            policy.get('capability_modes'),
            tool_name=tool_name,
            required_scopes=required_scopes,
        )

    def resolve_from_policy(
        self,
        default_mode: str,
        capability_modes: dict | None,
        *,
        tool_name: str,
        required_scopes: Sequence[str] | None,
    ) -> str:
        """纯判定：给**已按请求预取策略**的调用面用（AgentContext，避免逐工具重复取库）。

        聚合「工具名 override + 各 required_scope」取最严一档（见 scope_policy）。
        """
        return resolve_tool_mode(
            default_mode,
            capability_modes,
            tool_name=tool_name,
            required_scopes=list(required_scopes or []),
        )


capability_guard = CapabilityGuard()
