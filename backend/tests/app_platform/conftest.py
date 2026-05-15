"""App Platform 测试配置

使用真实 PostgreSQL 数据库进行集成测试，测试前后清理数据。
"""
from __future__ import annotations

import os
import sys
from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.app_platform.model import (
    AppDataRecords,
    AppDevelopers,
    AppInstallations,
    AppManifests,
    AppPermissionAuditLogs,
    AppPermissionGrants,
    AppScopes,
    AppVersions,
    PlatformScopes,
)
from backend.database.db import create_database_url


class FakeRedis:
    """模拟 Redis 客户端"""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    async def exists(self, key: str) -> bool:
        return key in self.values

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def setex(self, key: str, seconds: int, value: str) -> None:
        self.values[key] = value
        self.ttls[key] = seconds

    async def incr(self, key: str) -> int:
        current = int(self.values.get(key, '0'))
        current += 1
        self.values[key] = str(current)
        return current

    async def expire(self, key: str, seconds: int) -> bool:
        if key in self.values:
            self.ttls[key] = seconds
            return True
        return False

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)
        self.ttls.pop(key, None)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话，测试后回滚"""
    # 使用主数据库（不使用测试数据库，因为测试数据库可能不存在）
    db_url = create_database_url(unittest=False)
    engine = create_async_engine(db_url, echo=False, future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async with sessionmaker() as session:
        # 开启事务
        async with session.begin():
            try:
                yield session
                # 测试后回滚事务（不提交任何更改）
                await session.rollback()
            except Exception:
                await session.rollback()
                raise

    await engine.dispose()


@pytest_asyncio.fixture
async def redis_client() -> FakeRedis:
    """提供模拟 Redis 客户端"""
    return FakeRedis()


@pytest_asyncio.fixture
async def test_owner_id() -> str:
    """测试用 owner_id"""
    return 'test_owner_001'


@pytest_asyncio.fixture
async def test_user_id() -> str:
    """测试用 user_id"""
    return 'test_user_001'


@pytest_asyncio.fixture
async def test_app_id() -> str:
    """测试用 app_id"""
    return 'test_app_001'


@pytest_asyncio.fixture
async def cleanup_test_data(db_session: AsyncSession):
    """清理测试数据（实际上不需要，因为使用事务回滚）"""
    yield
    # 事务会自动回滚，不需要手动清理
