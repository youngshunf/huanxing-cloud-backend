"""
社区模块（hasn_community）集成测试基础设施。

- 复用项目 async_engine，连真实本地 PostgreSQL（127.0.0.1:15432/huanxing）。
- 每个用例在外层事务内运行，session 用 create_savepoint 模式：
  即使被测 service 调用 commit() 也只是释放 savepoint，结束后整体回滚，
  绝不污染数据库（符合"零 Mock 零 Fake"：连真库但不留痕）。
- 提供 human/agent 种子助手，便于构造作者/主人关系。
"""
from __future__ import annotations

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from backend.database.db import SQLALCHEMY_DATABASE_URL, uuid4_str


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    """事务隔离的 AsyncSession（用例结束自动回滚）。

    每个用例新建一个 NullPool engine：pytest-asyncio strict 模式下每个 async
    用例是独立 event loop，复用全局连接池会触发 "Event loop is closed"。
    """
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
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


async def seed_human(
    db: AsyncSession,
    *,
    nickname: str = '测试用户',
    user_id: int | None = None,
) -> dict:
    """插入一个 hasn_humans 行，返回 {hasn_id, user_id, nickname}。"""
    hasn_id = f'h_{uuid4_str()[:20]}'
    star_id = f's_{uuid4_str()[:12]}'
    uid = user_id if user_id is not None else int(uuid4_str().replace('-', '')[:8], 16) % 1_000_000_000
    await db.execute(
        text(
            'INSERT INTO hasn_humans (hasn_id, star_id, user_id, nickname, avatar, bio, status, '
            'contact_policy, tags, stats, created_time, updated_time) '
            "VALUES (:hasn_id, :star_id, :user_id, :nickname, '', '', 'active', "
            "'{}'::jsonb, ARRAY[]::varchar[], '{}'::jsonb, now(), now())"
        ),
        {'hasn_id': hasn_id, 'star_id': star_id, 'user_id': uid, 'nickname': nickname},
    )
    await db.flush()
    return {'hasn_id': hasn_id, 'user_id': uid, 'nickname': nickname, 'star_id': star_id}


async def seed_agent(
    db: AsyncSession,
    *,
    owner_hasn_id: str,
    display_name: str = '测试分身',
    capability_summary_json: dict | None = None,
    profile_json: dict | None = None,
) -> dict:
    """插入一个 hasn_agents 行（owner_id 指向 owner_hasn_id），返回 {hasn_id, ...}。"""
    import json

    hasn_id = f'a_{uuid4_str()[:20]}'
    star_id = f's_{uuid4_str()[:12]}'
    await db.execute(
        text(
            'INSERT INTO hasn_agents (hasn_id, star_id, owner_id, agent_name, display_name, '
            'type, role, status, created_via, api_key_hash, avatar, bio, '
            'capability_summary_json, profile_json, social_enabled, created_time, updated_time) '
            "VALUES (:hasn_id, :star_id, :owner_id, :agent_name, :display_name, "
            "'agent', 'assistant', 'active', 'test', :api_key_hash, '', '', "
            'CAST(:cap AS jsonb), CAST(:profile AS jsonb), true, now(), now())'
        ),
        {
            'hasn_id': hasn_id,
            'star_id': star_id,
            'owner_id': owner_hasn_id,
            'agent_name': display_name[:30],
            'display_name': display_name,
            'api_key_hash': uuid4_str().replace('-', '')[:64],
            'cap': json.dumps(capability_summary_json or {}),
            'profile': json.dumps(profile_json or {}),
        },
    )
    await db.flush()
    return {'hasn_id': hasn_id, 'owner_hasn_id': owner_hasn_id, 'display_name': display_name}


async def seed_post(
    db: AsyncSession,
    *,
    author_hasn_id: str,
    author_type: str = 'human',
    owner_hasn_id: str | None = None,
    content: str = '测试帖子',
    status: str = 'published',
    published_time=None,
    like_count: int = 0,
    tags: list[str] | None = None,
) -> str:
    """插入一个 hasn_posts 行，返回 post_id。published_time 可传 datetime 控制游标顺序。"""
    from backend.utils.timezone import timezone as _tz

    post_id = f'p_{uuid4_str()[:12]}'
    pt = published_time if published_time is not None else _tz.now()
    tag_literal = (
        'ARRAY[' + ','.join(f"'{t}'" for t in tags) + ']::varchar[]'
        if tags
        else 'ARRAY[]::varchar[]'
    )
    await db.execute(
        text(
            'INSERT INTO hasn_posts (post_id, author_type, author_hasn_id, owner_hasn_id, '
            'origin_workspace_kind, origin_workspace_id, content, tags, skill_tags, visibility, '
            'comment_policy, generation_type, status, like_count, comment_count, collect_count, '
            'share_count, created_time, updated_time, published_time) '
            "VALUES (:post_id, :author_type, :author_hasn_id, :owner_hasn_id, 'personal', '0', "
            f':content, {tag_literal}, ARRAY[]::varchar[], '
            "'public', 'all', :gen, :status, :like_count, 0, 0, 0, now(), now(), :published_time)"
        ),
        {
            'post_id': post_id,
            'author_type': author_type,
            'author_hasn_id': author_hasn_id,
            'owner_hasn_id': owner_hasn_id or author_hasn_id,
            'content': content,
            'gen': 'human' if author_type == 'human' else 'agent',
            'status': status,
            'like_count': like_count,
            'published_time': pt,
        },
    )
    await db.flush()
    return post_id


async def seed_collection_item(
    db: AsyncSession,
    *,
    owner_hasn_id: str,
    target_type: str,
    target_id: str,
) -> str:
    """为 owner 建一个收藏夹并放入一项，返回 collection_id。"""
    collection_id = f'col_{uuid4_str()[:12]}'
    await db.execute(
        text(
            'INSERT INTO hasn_collections (collection_id, owner_hasn_id, name, is_public, '
            "item_count, create_time, update_time) "
            "VALUES (:cid, :owner, '默认收藏夹', false, 1, now(), now())"
        ),
        {'cid': collection_id, 'owner': owner_hasn_id},
    )
    await db.execute(
        text(
            'INSERT INTO hasn_collection_items (collection_id, target_type, target_id, '
            'create_time, updated_time) VALUES (:cid, :tt, :tid, now(), now())'
        ),
        {'cid': collection_id, 'tt': target_type, 'tid': target_id},
    )
    await db.flush()
    return collection_id
