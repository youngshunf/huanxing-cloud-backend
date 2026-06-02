"""hasn_contact_requests 拆表 —— 真实 PostgreSQL 集成测试（零 mock）。

打本地真实库（端口 15432），验证 DB 级保证，对应 ADR 2026-05-30 第 6 节切片 2 验收：
- 部分唯一索引：同一对最多一条 pending（并发重复被挡）
- rejected 后可重新申请（不被部分唯一索引挡）
- accept 经 UPSERT 建双向 connected 边
- UPSERT 复活历史 archived 行（不新增行）
- 拉黑双向：对方拉黑我后 check_relation_permission 拒绝

每个用例独立 engine（NullPool，绑当前 event loop）+ 末尾 rollback，绝不污染真实库。
PG 不可达则 skip（非 mock 兜底）。
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from backend.app.hasn.api.v1.app.contacts import (
    list_pending_requests,
    respond_to_request,
    send_contact_request,
)
from backend.app.hasn.crud.crud_hasn_contact_requests import hasn_contact_requests_dao
from backend.app.hasn.crud.crud_hasn_contacts import hasn_contacts_dao
from backend.app.hasn.model import HasnContactRequests, HasnContacts, HasnHumans
from backend.app.hasn.schema.hasn_contacts_business import HasnContactRequestReq, HasnContactRespondReq
from backend.app.hasn.service.message_router import check_relation_permission
from backend.database.db import SQLALCHEMY_DATABASE_URL

pytestmark = pytest.mark.asyncio

# 独立测试身份（避免与真实数据/部分唯一索引碰撞；均 ≤36 字符）
A = 'h_creqit_aaaaaaaaaaaa'
B = 'h_creqit_bbbbbbbbbbbb'
REL = 'social'


@pytest_asyncio.fixture
async def pg_session():
    """每个用例独立 engine（NullPool 绑当前 loop）；不可达则 skip；末尾 rollback 不污染。"""
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
    except Exception as exc:
        await engine.dispose()
        pytest.skip(f'本地 PostgreSQL 不可达，跳过真实 PG 集成: {exc!r}')
    session = async_sessionmaker(engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


async def _count_pending(session, from_id: str, to_id: str) -> int:
    return await session.scalar(
        select(func.count())
        .select_from(HasnContactRequests)
        .where(HasnContactRequests.from_id == from_id)
        .where(HasnContactRequests.to_id == to_id)
        .where(HasnContactRequests.status == 'pending')
    )


async def test_partial_unique_blocks_second_pending(pg_session) -> None:
    """同一对 (from,to,social) 第二条 pending 触发部分唯一索引冲突。"""
    await hasn_contact_requests_dao.create_request(pg_session, from_id=A, to_id=B, to_owner_id=B)
    with pytest.raises(IntegrityError):
        async with pg_session.begin_nested():
            await hasn_contact_requests_dao.create_request(pg_session, from_id=A, to_id=B, to_owner_id=B)


async def test_rejected_does_not_block_re_request(pg_session) -> None:
    """拒绝后重新申请不被部分唯一索引挡（根治"拒绝后死锁"）。"""
    req = await hasn_contact_requests_dao.create_request(pg_session, from_id=A, to_id=B, to_owner_id=B)
    await hasn_contact_requests_dao.mark_rejected(pg_session, req.id, decided_by=B)
    await pg_session.flush()
    # rejected 后再发一条 pending —— 不应冲突
    await hasn_contact_requests_dao.create_request(pg_session, from_id=A, to_id=B, to_owner_id=B)
    await pg_session.flush()
    assert await _count_pending(pg_session, A, B) == 1  # 只有新这条 pending


async def test_upsert_revives_archived_contact(pg_session) -> None:
    """UPSERT 把历史 archived 行翻回 connected，而非新增行。"""
    archived = await hasn_contacts_dao.create_contact(
        pg_session, owner_id=A, peer_id=B, peer_type='human',
        relation_type=REL, trust_level=1, status='archived', channel_source='manual',
    )
    await pg_session.flush()
    revived = await hasn_contacts_dao.upsert_connected(
        pg_session, owner_id=A, peer_id=B, peer_type='human', relation_type=REL, trust_level=2,
    )
    assert revived.id == archived.id  # 同一行
    assert revived.status == 'connected'
    assert revived.trust_level == 2
    total = await pg_session.scalar(
        select(func.count()).select_from(HasnContacts)
        .where(HasnContacts.owner_id == A).where(HasnContacts.peer_id == B)
        .where(HasnContacts.relation_type == REL)
    )
    assert total == 1  # 没有新增第二行


async def test_upsert_builds_bidirectional_edges(pg_session) -> None:
    """accept 经两次 UPSERT 建出 A→B、B→A 双向 connected 边。"""
    await hasn_contacts_dao.upsert_connected(
        pg_session, owner_id=A, peer_id=B, peer_type='human', relation_type=REL, trust_level=2,
    )
    await hasn_contacts_dao.upsert_connected(
        pg_session, owner_id=B, peer_id=A, peer_type='human', relation_type=REL, trust_level=2,
    )
    fwd = await hasn_contacts_dao.get_relation(pg_session, A, B, REL)
    rev = await hasn_contacts_dao.get_relation(pg_session, B, A, REL)
    assert fwd is not None and fwd.status == 'connected' and fwd.trust_level == 2
    assert rev is not None and rev.status == 'connected' and rev.trust_level == 2


async def test_bidirectional_block_denies_messaging(pg_session) -> None:
    """对方（B）拉黑我（A）后，A→B 的 check_relation_permission 拒绝。"""
    # B 拉黑 A：B→A 行 trust_level=0
    await hasn_contacts_dao.create_contact(
        pg_session, owner_id=B, peer_id=A, peer_type='human',
        relation_type=REL, trust_level=0, status='blocked', channel_source='manual',
    )
    await pg_session.flush()
    result = await check_relation_permission(pg_session, sender_id=A, receiver_id=B)
    assert result['allowed'] is False
    assert result['reason'] == '已被对方拉黑'


async def test_block_denies_both_directions(pg_session) -> None:
    """对称：A 拉黑 B 后，B→A 方向也被拒（任一方向 blocked 都拦）。"""
    await hasn_contacts_dao.create_contact(
        pg_session, owner_id=A, peer_id=B, peer_type='human',
        relation_type=REL, trust_level=0, status='blocked', channel_source='manual',
    )
    await pg_session.flush()
    result = await check_relation_permission(pg_session, sender_id=B, receiver_id=A)
    assert result['allowed'] is False
    assert result['reason'] == '已被对方拉黑'


# ─────────────────────────────────────────────────────────────────────────────
# 端点级 E2E：直接调真实端点函数（auth 仅 dict 非 mock）打真库，串起完整生命周期。
# 端点内部 db.commit() 改为 flush，统一末尾 rollback，绝不落库。
# ─────────────────────────────────────────────────────────────────────────────

A_STAR = 'creqit90001'
B_STAR = 'creqit90002'


@pytest_asyncio.fixture
async def pg_session_endpoint():
    """端点级 E2E 用：commit→flush（端点内部会 commit），末尾 rollback 不落库。"""
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
    except Exception as exc:
        await engine.dispose()
        pytest.skip(f'本地 PostgreSQL 不可达，跳过端点级 E2E: {exc!r}')
    session = async_sessionmaker(engine, expire_on_commit=False)()
    session.commit = session.flush  # 端点 commit 改 flush，事务末尾统一 rollback
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
        await engine.dispose()


# hasn_humans.user_id 有唯一索引，A/B 用不同高位值（避免撞真实数据与彼此）
_TEST_USER_IDS = {A: 90900001, B: 90900002}


async def _seed_human(session, hasn_id: str, star_id: str, nickname: str) -> None:
    session.add(HasnHumans(
        hasn_id=hasn_id, star_id=star_id, user_id=_TEST_USER_IDS.get(hasn_id, 90900009),
        nickname=nickname, status='active',
    ))
    await session.flush()


async def test_e2e_send_list_accept_builds_bidirectional_edges(pg_session_endpoint) -> None:
    """A 发 → B received 列表可见 → B accept → 双向 connected 边 + 请求 accepted+resulting_contact_id。"""
    session = pg_session_endpoint
    await _seed_human(session, A, A_STAR, 'Alice')
    await _seed_human(session, B, B_STAR, 'Bob')

    with patch('backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to', new=AsyncMock(return_value=True)):
        sent = await send_contact_request(
            obj_in=HasnContactRequestReq(target_star_id=B_STAR, message='交个朋友'),
            db=session, auth={'hasn_id': A},
        )
        request_id = sent.data['request_id']
        assert sent.data['status'] == 'pending'

        received = await list_pending_requests(db=session, auth={'hasn_id': B}, direction='received')
        assert any(it['request_id'] == request_id and it['from_peer']['hasn_id'] == A for it in received.data)

        sent_list = await list_pending_requests(db=session, auth={'hasn_id': A}, direction='sent')
        assert any(it['request_id'] == request_id and it['target']['hasn_id'] == B for it in sent_list.data)

        resp = await respond_to_request(
            request_id=request_id, obj_in=HasnContactRespondReq(action='accept'),
            db=session, auth={'hasn_id': B},
        )
    assert resp.data['status'] == 'connected'

    fwd = await hasn_contacts_dao.get_relation(session, A, B, REL)
    rev = await hasn_contacts_dao.get_relation(session, B, A, REL)
    assert fwd is not None and fwd.status == 'connected' and fwd.trust_level == 2
    assert rev is not None and rev.status == 'connected' and rev.trust_level == 2

    req = await hasn_contact_requests_dao.get(session, request_id)
    assert req.status == 'accepted'
    assert req.resulting_contact_id == fwd.id


async def test_e2e_reject_then_resend_succeeds(pg_session_endpoint) -> None:
    """A 发 → B reject → A 重新发成功（根治拒绝后死锁）。"""
    session = pg_session_endpoint
    await _seed_human(session, A, A_STAR, 'Alice')
    await _seed_human(session, B, B_STAR, 'Bob')

    with patch('backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to', new=AsyncMock(return_value=True)):
        sent = await send_contact_request(
            obj_in=HasnContactRequestReq(target_star_id=B_STAR, message='第一次'),
            db=session, auth={'hasn_id': A},
        )
        await respond_to_request(
            request_id=sent.data['request_id'], obj_in=HasnContactRespondReq(action='reject'),
            db=session, auth={'hasn_id': B},
        )
        # reject 后重新申请：不应被部分唯一索引挡
        resent = await send_contact_request(
            obj_in=HasnContactRequestReq(target_star_id=B_STAR, message='再试一次'),
            db=session, auth={'hasn_id': A},
        )
    assert resent.data['status'] == 'pending'
    assert resent.data['request_id'] != sent.data['request_id']


async def test_e2e_blocked_sender_cannot_request(pg_session_endpoint) -> None:
    """B 拉黑 A 后，A 发好友请求被拒（未被对方拉黑校验）。"""
    session = pg_session_endpoint
    await _seed_human(session, A, A_STAR, 'Alice')
    await _seed_human(session, B, B_STAR, 'Bob')
    # B 拉黑 A
    await hasn_contacts_dao.create_contact(
        session, owner_id=B, peer_id=A, peer_type='human',
        relation_type=REL, trust_level=0, status='blocked', channel_source='manual',
    )
    await session.flush()

    with patch('backend.app.hasn.api.v1.app.contacts.ws_router.push_message_to', new=AsyncMock(return_value=True)):
        await send_contact_request(
            obj_in=HasnContactRequestReq(target_star_id=B_STAR, message='hi'),
            db=session, auth={'hasn_id': A},
        )
    # 被拉黑：断言没有建出 pending 请求（send 返回 fail）
    pending = await hasn_contact_requests_dao.get_active_pending(session, A, B, REL)
    assert pending is None
