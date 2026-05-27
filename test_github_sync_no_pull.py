"""测试 GitHub 同步（跳过 git pull）"""
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
        print("开始 GitHub 同步（跳过 git pull）...")

        # 直接调用扫描和同步，跳过 git pull
        skills_data = await github_sync_service._scan_skills()
        print(f"扫描到 {len(skills_data)} 个技能")

        synced_count = 0
        failed_count = 0

        for i, skill_data in enumerate(skills_data):
            try:
                await github_sync_service._sync_skill(db, skill_data)
                synced_count += 1
                if (i + 1) % 10 == 0:
                    print(f"已同步 {i + 1}/{len(skills_data)} 个技能...")
            except Exception as e:
                failed_count += 1
                print(f"同步失败: {skill_data.get('skill_id')}: {e}")

        # 提交事务
        await db.commit()

        print(f"\n同步结果:")
        print(f"  成功: True")
        print(f"  已同步: {synced_count}")
        print(f"  失败: {failed_count}")

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(test_sync())
