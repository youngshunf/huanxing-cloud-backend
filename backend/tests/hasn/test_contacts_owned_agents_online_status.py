"""回归：联系人「TA 的 AI 分身」必须带真实在线状态。

根因（修复前）：联系人**列表**端点 `api/v1/app/contacts.py` 构造 owned_agents 时
只查 HasnAgents、不 JOIN HasnAgentRuntimeReports，online_status 一路默认 "unknown"，
导致 daemon→webui 头像没有在线状态点。

修复：列表端点与详情构造共用 `HasnContactsService.fetch_owned_agents_with_status`，
该方法 outer-join 每个 agent 最新一条运行时上报，输出 online_status / last_seen_at。

本单测不依赖真实数据库：mock `db.execute` 截获 SELECT 语句并喂入假结果行，
断言（1）查询确实 JOIN 运行时上报表并取 runtime_status/last_seen_at，
（2）映射把 runtime_status 透传为 online_status，无上报记录回退 "unknown"。
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from sqlalchemy.dialects.postgresql import dialect as pg_dialect

from backend.app.hasn.service.hasn_contacts_service import HasnContactsService


def _fake_agent(suffix: str) -> SimpleNamespace:
    return SimpleNamespace(
        hasn_id=f'a_{suffix}',
        star_id=f'star_{suffix}',
        display_name=f'分身{suffix}',
        agent_name=f'agent_{suffix}',
        avatar=None,
        type='desktop',
        role='specialist',
        bio=f'简介{suffix}',
    )


def _mock_db(rows: list[tuple]) -> tuple[MagicMock, list]:
    """构造 db，使 db.execute 返回 rows，并记录传入的 statement。"""
    captured: list = []
    result = MagicMock()
    result.all.return_value = rows

    async def fake_execute(stmt: object) -> MagicMock:
        captured.append(stmt)
        return result

    db = MagicMock()
    db.execute = AsyncMock(side_effect=fake_execute)
    return db, captured


@pytest.mark.asyncio
async def test_query_outer_joins_runtime_reports() -> None:
    """SELECT 应引用 hasn_agent_runtime_reports 并取 runtime_status / last_seen_at。"""
    db, captured = _mock_db(rows=[])

    await HasnContactsService.fetch_owned_agents_with_status(db, 'h_owner')

    assert len(captured) == 1, f'expected 1 select, got {len(captured)}'
    sql = str(captured[0].compile(dialect=pg_dialect())).lower()
    assert 'hasn_agent_runtime_reports' in sql, f'missing runtime-report join: {sql}'
    assert 'runtime_status' in sql
    assert 'last_seen_at' in sql
    # 只取 social_enabled 且未删除的 active Agent（与详情构造一致，避免泄露）。
    assert 'social_enabled' in sql
    assert 'deleted_at' in sql


@pytest.mark.asyncio
async def test_maps_runtime_status_to_online_status() -> None:
    """有上报 → online_status 透传该状态；无上报（None）→ 回退 "unknown"。"""
    seen_at = datetime(2026, 6, 2, 8, 30, tzinfo=timezone.utc)
    rows = [
        (_fake_agent('online'), 'online', seen_at),
        (_fake_agent('offline'), 'offline', seen_at),
        (_fake_agent('noreport'), None, None),
    ]
    db, _ = _mock_db(rows)

    agents = await HasnContactsService.fetch_owned_agents_with_status(db, 'h_owner')

    assert [a['online_status'] for a in agents] == ['online', 'offline', 'unknown']
    # last_seen_at: 有则 ISO 字符串，无则 None。
    assert agents[0]['last_seen_at'] == seen_at.isoformat()
    assert agents[2]['last_seen_at'] is None
    # bio / 基础字段一并带出（卡片展示简介所依赖）。
    assert agents[0]['bio'] == '简介online'
    assert agents[0]['name'] == '分身online'
