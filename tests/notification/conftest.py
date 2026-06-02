"""统一通知服务（app/notification）集成测试基础设施。

- 连真实本地 PostgreSQL（127.0.0.1:15432/huanxing），事务回滚隔离（零 Mock 零 Fake）。
- 复用社区 conftest 的 seed_human/seed_agent；偏好行用本地 helper 直插。
"""
from __future__ import annotations

import pytest_asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from backend.database.db import SQLALCHEMY_DATABASE_URL

# 复用社区种子助手（同一套真库种子约定）
from tests.hasn_community.conftest import seed_agent as seed_agent
from tests.hasn_community.conftest import seed_human as seed_human


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    """事务隔离的 AsyncSession（用例结束自动回滚）。"""
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


async def seed_preference(
    db: AsyncSession,
    *,
    owner_id: str,
    category: str = '*',
    channels: dict | None = None,
    dnd: dict | None = None,
) -> None:
    """直插一条偏好行。"""
    import json

    await db.execute(
        text(
            'INSERT INTO hasn_notification_preferences (owner_id, category, channels, dnd, '
            'created_time, updated_time) VALUES (:owner, :cat, CAST(:ch AS jsonb), '
            'CAST(:dnd AS jsonb), now(), now())'
        ),
        {
            'owner': owner_id,
            'cat': category,
            'ch': json.dumps(channels or {}),
            'dnd': json.dumps(dnd or {}),
        },
    )
    await db.flush()
