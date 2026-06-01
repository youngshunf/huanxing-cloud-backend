"""ask 态批准闸门（D4，维度①）。

设计事实源：13-doc §3.1 / 93-doc §P6。
- 默认 **allow 无确认**；只有 owner 把某能力设为 `ask` 时，该能力**每次调用**才挂起→等待主人批准。
- **不按 risk 自动强制**：`risk_level` 仅 catalog/UI 提示，与是否挂起无关。
- 与维度②（关系可达性，工具内 `check_relation_permission`）正交：ask 不是关系确认。

机制：挂起时写一条 pending 请求（Redis，供主人 UI 列出 + daemon 推送）+ 审计；随后等待
主人决定（Redis 决定键，由 P7 daemon/主人 WebUI 回写）。approved→放行执行；rejected/超时→拒绝 + 审计。
零 fake：无决定即超时拒绝，绝不默认放行。
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid

from typing import TYPE_CHECKING, Any

from backend.database.redis import redis_client

if TYPE_CHECKING:
    from backend.app.mcp.auth import AgentContext

logger = logging.getLogger(__name__)

_PENDING_KEY = 'agent_ask:pending:{agent_hasn_id}'  # hash: request_id -> pending json
_DECISION_KEY = 'agent_ask:decision:{request_id}'  # str: 'approved' | 'rejected'

DECISION_APPROVED = 'approved'
DECISION_REJECTED = 'rejected'
DECISION_TIMEOUT = 'timeout'


def _safe_json(value: Any) -> dict[str, Any] | None:
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


class AskApprovalGate:
    """ask 态闸门：挂起 + 等待主人批准。"""

    def __init__(self, *, timeout_seconds: int = 120, poll_interval: float = 1.0, pending_ttl: int = 300) -> None:
        self._timeout_seconds = timeout_seconds
        self._poll_interval = poll_interval
        self._pending_ttl = pending_ttl

    async def gate(self, agent_context: AgentContext, *, tool_name: str, arguments: dict[str, Any]) -> None:
        """ask 态主路径：挂起→等待→放行/拒绝。approved 返回（执行继续）；否则 raise PermissionError。"""
        request_id = uuid.uuid4().hex
        await self._record_pending(agent_context, request_id, tool_name, arguments)
        decision = await self._await_decision(agent_context.agent_hasn_id, request_id)
        await self._finalize(agent_context, request_id, decision, tool_name)
        if decision != DECISION_APPROVED:
            raise PermissionError(f'Owner approval required (ask mode, {decision}) for tool: {tool_name}')

    async def _record_pending(
        self, agent_context: AgentContext, request_id: str, tool_name: str, arguments: dict[str, Any]
    ) -> None:
        """写 pending 请求（Redis 供主人列出/推送）+ 审计挂起。两者各自 best-effort，不互相阻断。"""
        payload = {
            'request_id': request_id,
            'agent_hasn_id': agent_context.agent_hasn_id,
            'owner_hasn_id': agent_context.owner_hasn_id,
            'tool_name': tool_name,
            'arguments': arguments,
        }
        try:
            key = _PENDING_KEY.format(agent_hasn_id=agent_context.agent_hasn_id)
            await redis_client.hset(key, request_id, json.dumps(payload, ensure_ascii=False))
            await redis_client.expire(key, self._pending_ttl)
        except Exception:
            logger.exception('Failed to persist ask-mode pending request to Redis')
        await self._audit(agent_context, 'mcp_ask_pending', request_id, tool_name, {'arguments': arguments})

    async def _await_decision(self, agent_hasn_id: str, request_id: str) -> str:
        """轮询主人决定键直至超时（默认 120s）。seam：测试可 monkeypatch 本方法即时返回决定。"""
        key = _DECISION_KEY.format(request_id=request_id)
        waited = 0.0
        while waited < self._timeout_seconds:
            try:
                value = await redis_client.get(key)
            except Exception:
                logger.exception('Failed to read ask-mode decision from Redis')
                return DECISION_TIMEOUT
            if value in (DECISION_APPROVED, DECISION_REJECTED):
                return value
            await asyncio.sleep(self._poll_interval)
            waited += self._poll_interval
        return DECISION_TIMEOUT

    async def _finalize(self, agent_context: AgentContext, request_id: str, decision: str, tool_name: str) -> None:
        """清理 pending + 决定键，审计最终决定。"""
        try:
            await redis_client.hdel(_PENDING_KEY.format(agent_hasn_id=agent_context.agent_hasn_id), request_id)
            await redis_client.delete(_DECISION_KEY.format(request_id=request_id))
        except Exception:
            logger.exception('Failed to clean up ask-mode keys')
        await self._audit(agent_context, 'mcp_ask_decision', request_id, tool_name, {'decision': decision})

    async def _audit(
        self, agent_context: AgentContext, action: str, request_id: str, tool_name: str, extra: dict[str, Any]
    ) -> None:
        try:
            from backend.app.hasn.service.hasn_audit_log_service import HasnAuditLogService
            from backend.database.db import async_db_session

            async with async_db_session() as db:
                await HasnAuditLogService().append(
                    db=db,
                    actor_type='agent',
                    actor_id=agent_context.agent_hasn_id,
                    action=action,
                    target_type='tool',
                    target_id=tool_name,
                    details={'request_id': request_id, 'tool_name': tool_name, **extra},
                )
        except Exception:
            logger.exception('Failed to audit ask-mode event %s', action)

    # —— owner 侧操作（P7 daemon 代理 / P8 webui 调用）——

    async def list_pending(self, agent_hasn_id: str) -> list[dict[str, Any]]:
        """列出某 Agent 当前挂起的 ask 请求（主人 UI 用）。"""
        try:
            raw = await redis_client.hgetall(_PENDING_KEY.format(agent_hasn_id=agent_hasn_id))
        except Exception:
            logger.exception('Failed to list ask-mode pending requests')
            return []
        return [parsed for value in (raw or {}).values() if (parsed := _safe_json(value)) is not None]

    async def submit_decision(self, request_id: str, decision: str) -> None:
        """主人对某挂起请求做决定（approve/reject）。daemon(P7)/webui(P8) 回写。"""
        normalized = DECISION_APPROVED if decision in (DECISION_APPROVED, 'approve') else DECISION_REJECTED
        await redis_client.setex(_DECISION_KEY.format(request_id=request_id), self._pending_ttl, normalized)


ask_approval_gate = AskApprovalGate()
