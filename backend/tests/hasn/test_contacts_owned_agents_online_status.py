"""回归：联系人「TA 的 AI 分身」必须带真实在线状态 + 正确描述。

在线状态来源：HasnAgents.online_status 列（心跳 last_heartbeat_at 更新的权威
字段，online/offline），**不是**空置的 HasnAgentRuntimeReports 表——后者对多数
agent 无任何行，曾导致头像永远显示离线灰点。
描述来源：HasnAgents.description（agent 角色介绍，bio 多为空）。

列表端点与详情构造共用 HasnContactsService.fetch_owned_agents_with_status，
保证集合 / 在线状态 / 描述三者一致。

本单测不依赖真实数据库：mock db.execute 截获 SELECT 并喂入假 agent 行，
断言（1）查询直接从 hasn_agents 过滤 social_enabled，不 JOIN 运行时上报表；
（2）映射把 online_status / description / last_heartbeat_at 正确带出。
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from sqlalchemy.dialects.postgresql import dialect as pg_dialect

from backend.app.hasn.service.hasn_contacts_service import HasnContactsService


def _fake_agent(suffix: str, online_status: str, heartbeat: datetime | None) -> SimpleNamespace:
    return SimpleNamespace(
        hasn_id=f'a_{suffix}',
        star_id=f'star_{suffix}',
        display_name=f'分身{suffix}',
        agent_name=f'agent_{suffix}',
        avatar=None,
        type='desktop',
        role='specialist',
        description=f'角色描述{suffix}',
        bio='',
        online_status=online_status,
        last_heartbeat_at=heartbeat,
    )


def _mock_db(agents: list) -> tuple[MagicMock, list]:
    """构造 db，使 db.execute(...).scalars().all() 返回 agents，并记录 statement。"""
    captured: list = []
    scalars = MagicMock()
    scalars.all.return_value = agents
    result = MagicMock()
    result.scalars.return_value = scalars

    async def fake_execute(stmt: object) -> MagicMock:
        captured.append(stmt)
        return result

    db = MagicMock()
    db.execute = AsyncMock(side_effect=fake_execute)
    return db, captured


@pytest.mark.asyncio
async def test_query_filters_hasn_agents_without_runtime_reports_join() -> None:
    """SELECT 应直接从 hasn_agents 过滤 social_enabled，不引用运行时上报表。"""
    db, captured = _mock_db(agents=[])

    await HasnContactsService.fetch_owned_agents_with_status(db, 'h_owner')

    assert len(captured) == 1, f'expected 1 select, got {len(captured)}'
    sql = str(captured[0].compile(dialect=pg_dialect())).lower()
    assert 'hasn_agents' in sql
    assert 'social_enabled' in sql
    assert 'deleted_at' in sql
    # 不再 JOIN 空置的运行时上报表。
    assert 'hasn_agent_runtime_reports' not in sql, f'unexpected runtime-report join: {sql}'


@pytest.mark.asyncio
async def test_maps_online_status_and_description_from_agent_row() -> None:
    """online_status 取自 agent 列；None→offline；description 与 last_seen_at 带出。"""
    beat = datetime(2026, 6, 2, 10, 14, tzinfo=timezone.utc)
    agents = [
        _fake_agent('on', 'online', beat),
        _fake_agent('off', 'offline', beat),
        _fake_agent('none', None, None),
    ]
    db, _ = _mock_db(agents)

    out = await HasnContactsService.fetch_owned_agents_with_status(db, 'h_owner')

    assert [a['online_status'] for a in out] == ['online', 'offline', 'offline']
    assert out[0]['description'] == '角色描述on'
    assert out[0]['last_seen_at'] == beat.isoformat()
    assert out[2]['last_seen_at'] is None
    assert out[0]['name'] == '分身on'
