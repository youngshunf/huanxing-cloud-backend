"""Agent MCP 接入凭证签发/吊销/校验集成测试（P1）。

连真实本地 PostgreSQL（127.0.0.1:15432/huanxing），savepoint 事务隔离，
结束整体回滚不留痕（符合"零 Mock 零 Fake"：连真库但不污染）。

验收（设计文档 12-Agent接入凭证设计.md §10 P1）：
- 签发返回完整明文 key 一次，库内只存 SHA-256 哈希（无明文列）；
- 吊销即时失效（吊销后再校验该 key 必拒）。
"""

from __future__ import annotations

import pytest
import pytest_asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from backend.app.hasn.crud.crud_hasn_agent_mcp_keys import hasn_agent_mcp_keys_dao
from backend.app.hasn.schema.hasn_agent_mcp_keys import IssueAgentMcpKeyParam
from backend.app.hasn.service.hasn_agent_mcp_keys_service import KEY_PREFIX, hasn_agent_mcp_keys_service
from backend.app.llm.core.encryption import key_encryption
from backend.common.exception import errors
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


async def _seed_user(db: AsyncSession, *, nickname: str) -> int:
    """落一个真实 sys_user（owner_user_id 外键依赖它），返回自增 id。"""
    uname = f'mcpkey_{uuid4_str()[:12]}'
    uid = (
        await db.execute(
            text(
                'INSERT INTO sys_user (uuid, username, nickname, status, is_superuser, is_staff, '
                'is_multi_login, join_time, created_time) '
                'VALUES (:uuid, :username, :nickname, 1, false, false, false, now(), now()) '
                'RETURNING id'
            ),
            {'uuid': uuid4_str(), 'username': uname, 'nickname': nickname},
        )
    ).scalar_one()
    await db.flush()
    return int(uid)


async def _seed_human(db: AsyncSession, *, nickname: str = 'MCPKey主人') -> tuple[str, int]:
    uid = await _seed_user(db, nickname=nickname)
    hasn_id = f'h_{uuid4_str()[:20]}'
    star_id = f's_{uuid4_str()[:12]}'
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
    return hasn_id, uid


async def _seed_agent(db: AsyncSession, *, owner_id: str, display_name: str = '分身') -> str:
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
async def test_issue_returns_plaintext_once_and_stores_only_hash(db: AsyncSession) -> None:
    """签发返回完整明文 key 一次；库内只存哈希，不存明文，哈希=SHA-256(明文)。"""
    owner_id, uid = await _seed_human(db)
    agent_id = await _seed_agent(db, owner_id=owner_id)

    issued = await hasn_agent_mcp_keys_service.issue(
        db,
        obj=IssueAgentMcpKeyParam(agent_hasn_id=agent_id, scopes=['hasn.memory.read']),
        owner_hasn_id=owner_id,
        owner_user_id=uid,
    )

    # 明文一次：返回完整 key，带正确前缀
    assert issued.key.startswith(f'{KEY_PREFIX}_'), issued.key
    assert issued.key_prefix == issued.key[:16]
    assert issued.status == 'active'
    assert issued.scopes == ['hasn.memory.read']

    # 库存哈希：DB 行的 key_hash 等于 SHA-256(明文)，且行上不存在明文列
    row = await hasn_agent_mcp_keys_dao.get(db, issued.id)
    assert row is not None
    assert row.key_hash == key_encryption.hash_key(issued.key)
    assert row.key_hash != issued.key  # 哈希 != 明文
    assert not hasattr(row, 'key'), 'ORM 行不得持有明文 key 列'
    assert not hasattr(row, 'key_encrypted'), '本表不可逆，不应有可解密密文列'


@pytest.mark.asyncio
async def test_verify_active_then_revoke_invalidates(db: AsyncSession) -> None:
    """active key 校验通过；吊销后再校验同一 key 必拒（吊销即失效）。"""
    owner_id, uid = await _seed_human(db)
    agent_id = await _seed_agent(db, owner_id=owner_id)
    issued = await hasn_agent_mcp_keys_service.issue(
        db,
        obj=IssueAgentMcpKeyParam(agent_hasn_id=agent_id),
        owner_hasn_id=owner_id,
        owner_user_id=uid,
    )

    # 吊销前：校验命中，返回对应行
    record = await hasn_agent_mcp_keys_service.verify(db, presented_key=issued.key)
    assert record.id == issued.id
    assert record.agent_hasn_id == agent_id

    # 吊销
    await hasn_agent_mcp_keys_service.revoke(db, pk=issued.id, owner_hasn_id=owner_id)
    revoked = await hasn_agent_mcp_keys_dao.get(db, issued.id)
    assert revoked is not None and revoked.status == 'revoked'

    # 吊销后：同一 key 校验被拒
    with pytest.raises(errors.AuthorizationError):
        await hasn_agent_mcp_keys_service.verify(db, presented_key=issued.key)


@pytest.mark.asyncio
async def test_issue_forbidden_for_unowned_agent(db: AsyncSession) -> None:
    """不能为不属于自己的 Agent 签发凭证（HASN：所有 Agent 必须有主人）。"""
    owner_a, _ = await _seed_human(db, nickname='ownerA')
    owner_b, uid_b = await _seed_human(db, nickname='ownerB')
    agent_of_a = await _seed_agent(db, owner_id=owner_a)

    with pytest.raises(errors.ForbiddenError):
        await hasn_agent_mcp_keys_service.issue(
            db,
            obj=IssueAgentMcpKeyParam(agent_hasn_id=agent_of_a),
            owner_hasn_id=owner_b,
            owner_user_id=uid_b,
        )


@pytest.mark.asyncio
async def test_node_binding_enforced(db: AsyncSession) -> None:
    """node 绑定默认开：错 node 拒、对 node 通过；不绑定（None）则任意 node 通过。"""
    owner_id, uid = await _seed_human(db)
    agent_id = await _seed_agent(db, owner_id=owner_id)

    bound = await hasn_agent_mcp_keys_service.issue(
        db,
        obj=IssueAgentMcpKeyParam(agent_hasn_id=agent_id, node_id='node-A'),
        owner_hasn_id=owner_id,
        owner_user_id=uid,
    )
    with pytest.raises(errors.AuthorizationError):
        await hasn_agent_mcp_keys_service.verify(db, presented_key=bound.key, node_id='node-B')
    ok = await hasn_agent_mcp_keys_service.verify(db, presented_key=bound.key, node_id='node-A')
    assert ok.id == bound.id

    unbound = await hasn_agent_mcp_keys_service.issue(
        db,
        obj=IssueAgentMcpKeyParam(agent_hasn_id=agent_id),
        owner_hasn_id=owner_id,
        owner_user_id=uid,
    )
    any_node = await hasn_agent_mcp_keys_service.verify(db, presented_key=unbound.key, node_id='whatever')
    assert any_node.id == unbound.id


@pytest.mark.asyncio
async def test_verify_unknown_key_rejected(db: AsyncSession) -> None:
    """未知 / 空 key 一律拒（零 fake：不静默放过）。"""
    with pytest.raises(errors.AuthorizationError):
        await hasn_agent_mcp_keys_service.verify(db, presented_key=f'{KEY_PREFIX}_bogusbogusbogus')
    with pytest.raises(errors.AuthorizationError):
        await hasn_agent_mcp_keys_service.verify(db, presented_key='')
