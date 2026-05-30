"""Owner 记忆合并服务集成测试（P4，ADR 2026-05-30 §5.4）。

连真实本地 PostgreSQL（127.0.0.1:15432/huanxing），用 savepoint 事务隔离，
结束整体回滚不留痕（符合"零 Mock 零 Fake"：连真库但不污染）。

LLM 合并走注入式 `llm_complete` 打桩（service 显式支持的测试接缝），
避免单测里打真实 new-api 网关——验证的是合并下发的 SQL 行为，不是 LLM 质量。
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from backend.app.hasn.model import HasnAgents, HasnOwnerMemory, HasnOwnerMemoryContribution
from backend.app.hasn.service.owner_memory_service import owner_memory_service
from backend.database.db import uuid4_str

# 本地开发数据库（与 tests/hasn/conftest.py 同源，刻意不依赖 .env，避免 worktree 落到 5432）
ASYNC_DATABASE_URL = 'postgresql+psycopg://mac@127.0.0.1:15432/huanxing'


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    """事务隔离的 AsyncSession（用例结束自动回滚，绝不污染真库）。"""
    engine = create_async_engine(ASYNC_DATABASE_URL, poolclass=NullPool)
    conn = await engine.connect()
    trans = await conn.begin()
    session = AsyncSession(
        bind=conn,
        expire_on_commit=False,
        join_transaction_mode='create_savepoint',
    )
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()


async def _seed_human(db: AsyncSession, *, nickname: str = 'P4主人') -> str:
    hasn_id = f'h_{uuid4_str()[:20]}'
    star_id = f's_{uuid4_str()[:12]}'
    uid = int(uuid4_str().replace('-', '')[:8], 16) % 1_000_000_000
    await db.execute(
        text(
            'INSERT INTO hasn_humans (hasn_id, star_id, user_id, nickname, avatar, bio, status, '
            'contact_policy, tags, stats, created_time, updated_time) '
            "VALUES (:hasn_id, :star_id, :uid, :nickname, '', '', 'active', "
            "'{}'::jsonb, ARRAY[]::varchar[], '{}'::jsonb, now(), now())"
        ),
        {'hasn_id': hasn_id, 'star_id': star_id, 'uid': uid, 'nickname': nickname},
    )
    await db.flush()
    return hasn_id


async def _seed_agent(db: AsyncSession, *, owner_id: str, display_name: str) -> str:
    hasn_id = f'a_{uuid4_str()[:20]}'
    star_id = f's_{uuid4_str()[:12]}'
    await db.execute(
        text(
            'INSERT INTO hasn_agents (hasn_id, star_id, owner_id, agent_name, display_name, '
            'api_key_hash, created_time) '
            'VALUES (:hasn_id, :star_id, :owner_id, :agent_name, :display_name, :api_key_hash, now())'
        ),
        {
            'hasn_id': hasn_id,
            'star_id': star_id,
            'owner_id': owner_id,
            'agent_name': display_name[:30],
            'display_name': display_name,
            'api_key_hash': uuid4_str().replace('-', '')[:64],
        },
    )
    await db.flush()
    return hasn_id


@pytest.mark.asyncio
async def test_merge_fans_out_to_all_owner_agents(db: AsyncSession) -> None:
    """两个 Agent 各贡献一条观察 -> 合并 -> owner_memory v1 + 两 Agent user_md 覆盖 + revision++。"""
    owner_id = await _seed_human(db)
    agent_a = await _seed_agent(db, owner_id=owner_id, display_name='分身A')
    agent_b = await _seed_agent(db, owner_id=owner_id, display_name='分身B')

    # 记录初始 revision（默认 1）
    rev_before = {
        row.hasn_id: row.profile_revision
        for row in (
            await db.execute(select(HasnAgents).where(HasnAgents.owner_id == owner_id))
        ).scalars().all()
    }
    assert rev_before == {agent_a: 1, agent_b: 1}

    r1 = await owner_memory_service.contribute(
        db, owner_id=owner_id, agent_hasn_id=agent_a, content='主人喜欢简洁的回答，常用中文。'
    )
    r2 = await owner_memory_service.contribute(
        db, owner_id=owner_id, agent_hasn_id=agent_b, content='主人是工程师，关注架构清晰度。'
    )
    assert r1['accepted'] is True
    assert r2['accepted'] is True

    captured: dict[str, list] = {}

    async def fake_llm(messages: list[dict[str, str]]) -> str:  # noqa: RUF029 - 必须 async 以匹配 LlmComplete 接口
        captured['messages'] = messages
        # 真实合并由 new-api 完成；此处确定性拼接，验证服务把观察传入并落库下发。
        return '# 主人\n- 偏好简洁中文回答\n- 工程师，关注架构清晰度'

    outcome = await owner_memory_service.merge_owner_memory(db, owner_id=owner_id, llm_complete=fake_llm)

    assert outcome['merged'] is True
    assert outcome['version'] == 1
    assert outcome['contributions_merged'] == 2
    assert outcome['agents_updated'] == 2

    # 观察确实被传入 LLM（合并提示里含两条贡献）
    user_msg = captured['messages'][-1]['content']
    assert '简洁的回答' in user_msg
    assert '工程师' in user_msg

    # owner_memory 落库 version=1
    mem = (
        await db.execute(select(HasnOwnerMemory).where(HasnOwnerMemory.owner_id == owner_id))
    ).scalar_one()
    assert mem.version == 1
    assert '架构清晰度' in mem.content
    assert mem.token_count and mem.token_count > 0

    # 两条贡献都被标 merged
    contribs = (
        await db.execute(
            select(HasnOwnerMemoryContribution).where(HasnOwnerMemoryContribution.owner_id == owner_id)
        )
    ).scalars().all()
    assert len(contribs) == 2
    assert all(c.status == 'merged' and c.merged_into_version == 1 for c in contribs)

    # 两个 Agent 的 user_md 被覆盖为合并内容 + profile_revision 自增
    agents = (
        await db.execute(select(HasnAgents).where(HasnAgents.owner_id == owner_id))
    ).scalars().all()
    assert len(agents) == 2
    for a in agents:
        assert a.user_md == mem.content
        assert a.profile_revision == rev_before[a.hasn_id] + 1

    # 下发读取一致
    served = await owner_memory_service.get_owner_memory(db, owner_id=owner_id)
    assert served['version'] == 1
    assert served['content'] == mem.content


@pytest.mark.asyncio
async def test_merge_no_pending_is_noop(db: AsyncSession) -> None:
    """没有 pending 贡献时合并是 no-op，不写 owner_memory、不动 Agent。"""
    owner_id = await _seed_human(db)
    agent = await _seed_agent(db, owner_id=owner_id, display_name='孤独分身')

    async def fail_llm(messages: list[dict[str, str]]) -> str:  # noqa: RUF029 - async 以匹配 LlmComplete 接口；本例不应被调用
        raise AssertionError('LLM should not be called when there is no pending contribution')

    outcome = await owner_memory_service.merge_owner_memory(db, owner_id=owner_id, llm_complete=fail_llm)
    assert outcome['merged'] is False
    assert outcome['version'] is None

    mem = (
        await db.execute(select(HasnOwnerMemory).where(HasnOwnerMemory.owner_id == owner_id))
    ).scalar_one_or_none()
    assert mem is None

    a = (await db.execute(select(HasnAgents).where(HasnAgents.hasn_id == agent))).scalar_one()
    assert a.profile_revision == 1
    assert a.user_md is None


@pytest.mark.asyncio
async def test_empty_contribution_rejected(db: AsyncSession) -> None:
    """空白观察被拒，不入库。"""
    owner_id = await _seed_human(db)
    agent = await _seed_agent(db, owner_id=owner_id, display_name='空贡献分身')

    res = await owner_memory_service.contribute(db, owner_id=owner_id, agent_hasn_id=agent, content='   ')
    assert res['accepted'] is False

    contribs = (
        await db.execute(
            select(HasnOwnerMemoryContribution).where(HasnOwnerMemoryContribution.owner_id == owner_id)
        )
    ).scalars().all()
    assert contribs == []


@pytest.mark.asyncio
async def test_list_contributions_orders_desc_and_counts_pending(db: AsyncSession) -> None:
    """owner 透明视图：贡献按时间倒序，pending_count 只数未合并。"""
    owner_id = await _seed_human(db)
    agent_a = await _seed_agent(db, owner_id=owner_id, display_name='分身A')
    agent_b = await _seed_agent(db, owner_id=owner_id, display_name='分身B')

    await owner_memory_service.contribute(db, owner_id=owner_id, agent_hasn_id=agent_a, content='观察一')
    await owner_memory_service.contribute(db, owner_id=owner_id, agent_hasn_id=agent_b, content='观察二')

    async def fake_llm(messages: list[dict[str, str]]) -> str:  # noqa: RUF029 - async 以匹配 LlmComplete 接口
        return '# 主人\n合并记忆'

    # 先合并这两条（变 merged），再追加一条 pending
    await owner_memory_service.merge_owner_memory(db, owner_id=owner_id, llm_complete=fake_llm)
    await owner_memory_service.contribute(db, owner_id=owner_id, agent_hasn_id=agent_a, content='观察三-新')

    listing = await owner_memory_service.list_contributions(db, owner_id=owner_id, limit=50)
    assert len(listing['items']) == 3
    # 倒序：最新（观察三-新）在最前
    assert listing['items'][0]['content'] == '观察三-新'
    assert listing['items'][0]['status'] == 'pending'
    # 只有 1 条 pending（另外两条已 merged）
    assert listing['pending_count'] == 1
    merged_items = [i for i in listing['items'] if i['status'] == 'merged']
    assert len(merged_items) == 2
    assert all(i['merged_into_version'] == 1 for i in merged_items)


@pytest.mark.asyncio
async def test_merge_empty_llm_output_raises_and_keeps_pending(db: AsyncSession) -> None:
    """LLM 返回空内容 -> 抛错且贡献保持 pending（不产生假合并）。"""
    owner_id = await _seed_human(db)
    agent = await _seed_agent(db, owner_id=owner_id, display_name='合并失败分身')
    await owner_memory_service.contribute(db, owner_id=owner_id, agent_hasn_id=agent, content='主人在深圳。')

    async def empty_llm(messages: list[dict[str, str]]) -> str:  # noqa: RUF029 - 必须 async 以匹配 LlmComplete 接口
        return '   '

    with pytest.raises(ValueError):
        await owner_memory_service.merge_owner_memory(db, owner_id=owner_id, llm_complete=empty_llm)

    # 贡献仍 pending，未被错误标记 merged
    contribs = (
        await db.execute(
            select(HasnOwnerMemoryContribution).where(HasnOwnerMemoryContribution.owner_id == owner_id)
        )
    ).scalars().all()
    assert len(contribs) == 1
    assert contribs[0].status == 'pending'
