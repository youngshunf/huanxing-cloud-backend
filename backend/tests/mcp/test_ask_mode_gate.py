"""P6 — ask 态批准闸门单测（D4，非 risk 强制）。

覆盖：
- gate() 自身：approved→放行；rejected/timeout→PermissionError。
- server.call_tool 接线：mode=ask→挂起(走 gate)；approved→执行、rejected→PermissionError；
  mode=allow→**不挂起**（gate 不被调用），即便工具 risk=high 也不挂起（验证非 risk 强制）。

零外部依赖：gate 的持久化/等待 seam 全 monkeypatch，不连 Redis/DB。
"""

from __future__ import annotations

from typing import Any

import pytest

from backend.app.mcp.ask_gate import (
    DECISION_APPROVED,
    DECISION_REJECTED,
    DECISION_TIMEOUT,
    AskApprovalGate,
)
from backend.app.mcp.auth import AgentContext
from backend.app.mcp.tools.base import BaseTool


class _StubTool(BaseTool):
    def __init__(self, *, risk: str = 'low') -> None:
        self._risk = risk

    @property
    def name(self) -> str:
        return 'hasn.stub.act'

    @property
    def description(self) -> str:
        return 'stub tool for ask-gate tests'

    @property
    def input_schema(self) -> dict[str, Any]:
        return {'type': 'object', 'properties': {}}

    @property
    def required_scopes(self) -> list[str]:
        return ['stub:act']

    @property
    def risk_level(self) -> str:
        return self._risk

    async def execute(self, agent_context: AgentContext, arguments: dict[str, Any]) -> dict[str, Any]:
        return {'executed': True}


def _ctx(*, default_mode: str = 'allow', capability_modes: dict | None = None) -> AgentContext:
    return AgentContext(
        hasn_id='a_ask_test',
        owner_id=0,
        scopes=[],
        agent_status='active',
        metadata={},
        owner_hasn_id='h_ask_test',
        session_uuid='amk_ask_test',
        default_mode=default_mode,
        capability_modes=capability_modes or {},
    )


def _gate_no_io(monkeypatch: pytest.MonkeyPatch, gate: AskApprovalGate) -> None:
    """掐断 gate 的 Redis/DB 持久化与审计 seam，仅保留决定逻辑。"""

    async def _noop(*args: object, **kwargs: object) -> None:  # noqa: RUF029
        return None

    monkeypatch.setattr(gate, '_record_pending', _noop)
    monkeypatch.setattr(gate, '_finalize', _noop)


@pytest.mark.asyncio
async def test_gate_approved_returns(monkeypatch: pytest.MonkeyPatch) -> None:
    gate = AskApprovalGate()
    _gate_no_io(monkeypatch, gate)

    async def _approved(*args: object, **kwargs: object) -> str:  # noqa: RUF029
        return DECISION_APPROVED

    monkeypatch.setattr(gate, '_await_decision', _approved)
    # 不抛 = 放行
    await gate.gate(_ctx(), tool_name='hasn.stub.act', arguments={})


@pytest.mark.asyncio
@pytest.mark.parametrize('decision', [DECISION_REJECTED, DECISION_TIMEOUT])
async def test_gate_not_approved_raises(monkeypatch: pytest.MonkeyPatch, decision: str) -> None:
    gate = AskApprovalGate()
    _gate_no_io(monkeypatch, gate)

    async def _decide(*args: object, **kwargs: object) -> str:  # noqa: RUF029
        return decision

    monkeypatch.setattr(gate, '_await_decision', _decide)
    with pytest.raises(PermissionError):
        await gate.gate(_ctx(), tool_name='hasn.stub.act', arguments={})


@pytest.mark.asyncio
async def test_call_tool_ask_mode_suspends_then_executes_on_approve(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.mcp import ask_gate as ask_gate_module
    from backend.app.mcp.server import HasnCloudMcpServer

    server = HasnCloudMcpServer()
    server.tool_registry.register(_StubTool())

    async def _noop_load(*args: object, **kwargs: object) -> None:  # noqa: RUF029
        return None

    monkeypatch.setattr(server, '_load_app_tools', _noop_load)
    monkeypatch.setattr(server, '_log_tool_call', _noop_load)

    called: dict[str, Any] = {}

    async def _gate(agent_context: object, *, tool_name: str, arguments: dict) -> None:  # noqa: RUF029
        called['gated'] = tool_name  # 批准（不抛）

    monkeypatch.setattr(ask_gate_module.ask_approval_gate, 'gate', _gate)

    ctx = _ctx(default_mode='allow', capability_modes={'stub:act': 'ask'})
    result = await server.call_tool(ctx, 'hasn.stub.act', {})
    assert result == {'executed': True}
    assert called['gated'] == 'hasn.stub.act'  # 确实走了挂起闸门


@pytest.mark.asyncio
async def test_call_tool_ask_mode_rejected_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.app.mcp import ask_gate as ask_gate_module
    from backend.app.mcp.server import HasnCloudMcpServer

    server = HasnCloudMcpServer()
    server.tool_registry.register(_StubTool())

    async def _noop_load(*args: object, **kwargs: object) -> None:  # noqa: RUF029
        return None

    monkeypatch.setattr(server, '_load_app_tools', _noop_load)
    monkeypatch.setattr(server, '_log_tool_call', _noop_load)

    async def _gate_reject(*args: object, **kwargs: object) -> None:  # noqa: RUF029
        raise PermissionError('rejected')

    monkeypatch.setattr(ask_gate_module.ask_approval_gate, 'gate', _gate_reject)

    ctx = _ctx(default_mode='allow', capability_modes={'stub:act': 'ask'})
    with pytest.raises(PermissionError):
        await server.call_tool(ctx, 'hasn.stub.act', {})


@pytest.mark.asyncio
@pytest.mark.parametrize('risk', ['low', 'high'])
async def test_call_tool_allow_mode_never_suspends(monkeypatch: pytest.MonkeyPatch, risk: str) -> None:
    """mode=allow 直接执行无挂起；high risk 但 allow 也不挂起（D4：非 risk 强制）。"""
    from backend.app.mcp import ask_gate as ask_gate_module
    from backend.app.mcp.server import HasnCloudMcpServer

    server = HasnCloudMcpServer()
    server.tool_registry.register(_StubTool(risk=risk))

    async def _noop_load(*args: object, **kwargs: object) -> None:  # noqa: RUF029
        return None

    monkeypatch.setattr(server, '_load_app_tools', _noop_load)
    monkeypatch.setattr(server, '_log_tool_call', _noop_load)

    async def _gate_must_not_be_called(*args: object, **kwargs: object) -> None:  # noqa: RUF029
        raise AssertionError('allow 模式不应挂起 ask 闸门')

    monkeypatch.setattr(ask_gate_module.ask_approval_gate, 'gate', _gate_must_not_be_called)

    ctx = _ctx(default_mode='allow', capability_modes={})  # 全 allow
    result = await server.call_tool(ctx, 'hasn.stub.act', {})
    assert result == {'executed': True}
