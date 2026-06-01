"""P9 — external MCP 结构预留回归（Q5：本轮只预留，不放开）。

断言三件事：
1. ToolSource 字面量含 'external'（契约预留）。
2. catalog external 分组存在但能力为空（不造假、不放连接器）。
3. server._dispatch_by_source 对 external 维持 P7 前「未实现」抛错（不静默成功）。

不建表、不连真实外部 MCP。
"""

from __future__ import annotations

import typing

import pytest

from backend.app.mcp.auth import AgentContext
from backend.app.mcp.errors import McpToolError
from backend.app.mcp.server import mcp_server
from backend.app.mcp.tool_directory import ToolSource


def _ctx() -> AgentContext:
    return AgentContext(
        hasn_id='a_external_reserved',
        owner_id=0,
        scopes=[],
        agent_status='active',
        metadata={},
        owner_hasn_id='h_external_reserved',
        session_uuid='catalog:a_external_reserved',
    )


def test_tool_source_literal_reserves_external() -> None:
    assert 'external' in typing.get_args(ToolSource)


def test_catalog_external_group_present_but_empty() -> None:
    catalog = mcp_server.tool_directory.build_scope_catalog(_ctx())
    by_source = {s['source']: s for s in catalog['sources']}
    assert 'external' in by_source, 'external 分组结构必须预留'
    assert by_source['external']['capabilities'] == [], 'external 本轮不放开 → 能力为空'


class _ExternalTool:
    name = 'hasn.ext.acme.do'
    source = 'external'
    required_scopes: list[str] = []

    async def execute(self, agent_context: AgentContext, arguments: dict) -> dict:
        return {'should_not_run': True}


@pytest.mark.asyncio
async def test_dispatch_external_raises_not_enabled() -> None:
    """external 来源在 P7 前云端无承接 → 抛 McpToolError，不静默成功。"""
    tool = _ExternalTool()
    with pytest.raises(McpToolError):
        await mcp_server._dispatch_by_source(_ctx(), tool, 'external', {})
