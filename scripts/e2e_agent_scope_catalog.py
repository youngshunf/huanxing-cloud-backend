"""93-doc E2E（backend 真实联调）：默认全开 + 动态目录 + D3 即时生效 + ask 闸门。

真实基础设施（零 mock）：本地 PostgreSQL(15432) + Redis(6379)。直接驱动 service/gate
（catalog 构建走真实工具注册表，update 走真实表写入 + 缓存失效，ask 走真实 Redis）。

跑法：
    DATABASE_PORT=15432 .venv/bin/python scripts/e2e_agent_scope_catalog.py
证据落 test-results/。
"""

from __future__ import annotations

import asyncio
import json
import sys

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from backend.app.hasn.service.agent_scopes_service import agent_scopes_service
from backend.app.mcp.ask_gate import DECISION_APPROVED, ask_approval_gate
from backend.app.mcp.auth import AgentContext
from backend.app.mcp.server import mcp_server
from backend.app.mcp.tools.message import MessageSendTool
from backend.common.security.agent_jwt import create_default_agent_scopes
from backend.database.db import async_db_session

EVIDENCE = Path('test-results/e2e_agent_scope_catalog.json')
steps: list[dict] = []


def record(name: str, ok: bool, detail: object = None) -> None:
    steps.append({'step': name, 'ok': ok, 'detail': detail})
    mark = 'PASS' if ok else 'FAIL'
    print(f'[{mark}] {name} :: {detail}')


async def _find_agent(db) -> tuple[str, str] | None:
    row = (
        await db.execute(
            text("SELECT hasn_id, owner_id FROM hasn_agents WHERE status = 'active' LIMIT 1")
        )
    ).first()
    return (row[0], row[1]) if row else None


async def _seed_owner_and_agent(db) -> tuple[str, str]:
    """无现成 agent 时，最小化播一个 owner(human)+agent，仅供 E2E 读取归属与策略。"""
    suffix = datetime.now(timezone.utc).strftime('%H%M%S')
    owner_hasn = f'h_e2e_scope_{suffix}'
    agent_hasn = f'a_e2e_scope_{suffix}'
    star = f'e2e{suffix}'
    await db.execute(
        text("""
            INSERT INTO hasn_humans (hasn_id, star_id, nickname, status, created_time, updated_time)
            VALUES (:h, :s, 'E2E Owner', 'active', NOW(), NOW())
            ON CONFLICT (hasn_id) DO NOTHING
        """),
        {'h': owner_hasn, 's': star},
    )
    await db.execute(
        text("""
            INSERT INTO hasn_agents
                (hasn_id, owner_id, star_id, display_name, agent_name, status, created_time, updated_time)
            VALUES (:a, :o, :s, '星诺E2E', 'assistant', 'active', NOW(), NOW())
            ON CONFLICT (hasn_id) DO NOTHING
        """),
        {'a': agent_hasn, 'o': owner_hasn, 's': f'{star}#agent'},
    )
    await db.commit()
    await create_default_agent_scopes(db, agent_hasn, owner_hasn)
    return agent_hasn, owner_hasn


def _platform_cap(catalog: dict, key: str) -> dict | None:
    for source in catalog['sources']:
        if source['source'] == 'platform':
            for cap in source['capabilities']:
                if cap['key'] == key:
                    return cap
    return None


async def main() -> int:
    seeded = False
    async with async_db_session() as db:
        found = await _find_agent(db)
        if found:
            agent_hasn, owner_hasn = found
            # 确保有 scopes 行
            await create_default_agent_scopes(db, agent_hasn, owner_hasn)
        else:
            agent_hasn, owner_hasn = await _seed_owner_and_agent(db)
            seeded = True
    record('discover/seed agent', True, {'agent': agent_hasn, 'owner': owner_hasn, 'seeded': seeded})

    # 先把状态归位到全 allow（清掉历史 override），保证可重复
    async with async_db_session() as db:
        await agent_scopes_service.update_agent_scopes(
            db, agent_hasn, owner_hasn,
            _req(default_mode='allow', capability_modes={}),
        )

    # 1) 默认全开 + 动态目录：catalog 含 platform 分组与 message:send=allow，external 预留空（Q5）
    async with async_db_session() as db:
        catalog = (await agent_scopes_service.get_scope_catalog(db, agent_hasn, owner_hasn)).model_dump()
    sources = {s['source'] for s in catalog['sources']}
    send = _platform_cap(catalog, 'message:send')
    ext = next((s for s in catalog['sources'] if s['source'] == 'external'), None)
    ok1 = (
        {'platform', 'app', 'external'} <= sources
        and send is not None
        and send['mode'] == 'allow'
        and ext is not None
        and ext['capabilities'] == []
    )
    record('default-all-allow + dynamic catalog + external reserved empty', ok1,
           {'sources': sorted(sources), 'message_send': send, 'external_empty': bool(ext and not ext['capabilities'])})

    # 2) D3 即时生效：把 message:send 设 deny → 不重签 → catalog 立刻 deny + MCP 工具被隐藏/拒绝
    async with async_db_session() as db:
        await agent_scopes_service.update_agent_scopes(
            db, agent_hasn, owner_hasn,
            _req(default_mode='allow', capability_modes={'message:send': 'deny'}),
        )
    async with async_db_session() as db:
        catalog2 = (await agent_scopes_service.get_scope_catalog(db, agent_hasn, owner_hasn)).model_dump()
    send2 = _platform_cap(catalog2, 'message:send')
    # 用现查策略构 AgentContext，验证 _can_discover / tool_mode 即时反映
    async with async_db_session() as db:
        from backend.common.security.agent_jwt import get_agent_scopes_cached

        cfg = await get_agent_scopes_cached(agent_hasn, db)
    ctx = AgentContext(
        hasn_id=agent_hasn, owner_id=0, scopes=[], agent_status='active', metadata={},
        owner_hasn_id=owner_hasn, session_uuid='e2e',
        default_mode=cfg['default_mode'], capability_modes=cfg['capability_modes'],
    )
    denied = ctx.is_tool_denied(MessageSendTool())
    ok2 = send2 is not None and send2['mode'] == 'deny' and denied is True
    record('D3 instant deny (no re-sign): catalog=deny + tool hidden/denied', ok2,
           {'catalog_mode': send2 and send2['mode'], 'is_tool_denied': denied})

    # 3) ask 闸门：设 ask → tool_mode=ask；真实 Redis pending + submit approve → gate 放行
    async with async_db_session() as db:
        await agent_scopes_service.update_agent_scopes(
            db, agent_hasn, owner_hasn,
            _req(default_mode='allow', capability_modes={'message:send': 'ask'}),
        )
        cfg3 = await __import__(
            'backend.common.security.agent_jwt', fromlist=['get_agent_scopes_cached']
        ).get_agent_scopes_cached(agent_hasn, db)
    ctx3 = AgentContext(
        hasn_id=agent_hasn, owner_id=0, scopes=[], agent_status='active', metadata={},
        owner_hasn_id=owner_hasn, session_uuid='e2e',
        default_mode=cfg3['default_mode'], capability_modes=cfg3['capability_modes'],
    )
    mode_ask = ctx3.tool_mode(MessageSendTool())

    # 真实 Redis：写 pending → list_pending 可见 → submit approve → _await_decision 返回 approved
    rid = 'e2e_ask_req_1'
    await ask_approval_gate._record_pending(ctx3, rid, 'hasn.message.send', {'to': 'h_x', 'content': 'hi'})
    pending = await ask_approval_gate.list_pending(agent_hasn)
    await ask_approval_gate.submit_decision(rid, 'approve')
    decision = await ask_approval_gate._await_decision(agent_hasn, rid)
    await ask_approval_gate._finalize(ctx3, rid, decision, 'hasn.message.send')
    ok3 = mode_ask == 'ask' and any(p.get('request_id') == rid for p in pending) and decision == DECISION_APPROVED
    record('ask gate: mode=ask + real Redis pending listed + approve resolves', ok3,
           {'tool_mode': mode_ask, 'pending_count': len(pending), 'decision': decision})

    # 复位 allow
    async with async_db_session() as db:
        await agent_scopes_service.update_agent_scopes(
            db, agent_hasn, owner_hasn, _req(default_mode='allow', capability_modes={}),
        )

    all_ok = all(s['ok'] for s in steps)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(
            {'all_ok': all_ok, 'agent': agent_hasn, 'owner': owner_hasn, 'steps': steps},
            ensure_ascii=False, indent=2,
        ),
        encoding='utf-8',
    )
    print(f'\nE2E {"PASSED" if all_ok else "FAILED"} — evidence: {EVIDENCE}')
    return 0 if all_ok else 1


def _req(*, default_mode: str, capability_modes: dict):
    from backend.app.hasn.schema.agent_scopes import UpdateAgentScopesRequest

    return UpdateAgentScopesRequest(default_mode=default_mode, capability_modes=capability_modes)


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
