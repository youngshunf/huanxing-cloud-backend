"""测试 GitHub 同步"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from backend.app.marketplace.service.github_sync_service import github_sync_service
from backend.core.conf import settings

async def test_sync():
    # 创建数据库引擎
    engine = create_async_engine(
        f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_SCHEMA}",
        echo=False
    )

    async with AsyncSession(engine) as db:
        print("开始 GitHub 同步...")
        result = await github_sync_service.sync_from_github(db, force=True)

        # 提交事务
        await db.commit()

        print(f"\n同步结果:")
        print(f"  成功: {result.get('success')}")
        print(f"  已同步: {result.get('synced', 0)}")
        print(f"  失败: {result.get('failed', 0)}")

        if result.get('errors'):
            print(f"\n错误列表 (前10个):")
            for error in result['errors'][:10]:
                print(f"  - {error}")

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(test_sync())
