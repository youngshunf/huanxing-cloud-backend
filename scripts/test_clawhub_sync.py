#!/usr/bin/env python3
"""
Test ClawHub sync service
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.marketplace.service.clawhub_sync_service import clawhub_sync_service
from backend.database.db import async_db_session


async def test_fetch_skills():
    """Test fetching skills from ClawHub"""
    print("=" * 60)
    print("测试从 ClawHub 获取技能")
    print("=" * 60)

    try:
        skills = await clawhub_sync_service._fetch_all_skills()
        print(f"✅ 成功获取 {len(skills)} 个技能")

        if skills:
            print(f"\n前 3 个技能：")
            for i, skill in enumerate(skills[:3], 1):
                print(f"\n{i}. {skill.get('displayName', 'N/A')}")
                print(f"   Slug: {skill.get('slug')}")
                print(f"   Summary: {skill.get('summary', 'N/A')[:80]}...")
                stats = skill.get('stats', {})
                print(f"   Downloads: {stats.get('downloads', 0)}, Stars: {stats.get('stars', 0)}")

    except Exception as e:
        print(f"❌ 获取技能失败: {e}")

    print()


async def test_filter_skills():
    """Test filtering skills"""
    print("=" * 60)
    print("测试技能过滤")
    print("=" * 60)

    try:
        skills = await clawhub_sync_service._fetch_all_skills()
        filtered = clawhub_sync_service._filter_skills(skills)

        print(f"✅ 原始技能数: {len(skills)}")
        print(f"✅ 过滤后技能数: {len(filtered)}")
        print(f"✅ 过滤条件: downloads >= {clawhub_sync_service.sync_filters['min_downloads']}, "
              f"stars >= {clawhub_sync_service.sync_filters['min_stars']}")

    except Exception as e:
        print(f"❌ 过滤技能失败: {e}")

    print()


async def test_sync_limited():
    """Test syncing limited skills"""
    print("=" * 60)
    print("测试同步前 5 个技能")
    print("=" * 60)

    try:
        async with async_db_session() as db:
            # Fetch and filter skills
            skills = await clawhub_sync_service._fetch_all_skills()
            filtered = clawhub_sync_service._filter_skills(skills)

            # Sync only first 5 skills
            limited_skills = filtered[:5]

            print(f"准备同步 {len(limited_skills)} 个技能...")

            synced_count = 0
            failed_count = 0
            errors = []

            for i, skill_data in enumerate(limited_skills, 1):
                slug = skill_data.get('slug', 'unknown')
                try:
                    print(f"\n[{i}/{len(limited_skills)}] 同步技能: {slug}")
                    await clawhub_sync_service._sync_skill(db, skill_data)
                    synced_count += 1
                    print(f"  ✅ 成功")
                except Exception as e:
                    failed_count += 1
                    error_msg = f"{slug}: {str(e)}"
                    errors.append(error_msg)
                    print(f"  ❌ 失败: {e}")

            await db.commit()

            print(f"\n同步完成:")
            print(f"  成功: {synced_count}")
            print(f"  失败: {failed_count}")

            if errors:
                print(f"\n错误列表:")
                for error in errors:
                    print(f"  - {error}")

    except Exception as e:
        print(f"❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()

    print()


async def test_full_sync():
    """Test full sync (use with caution)"""
    print("=" * 60)
    print("测试完整同步（所有符合条件的技能）")
    print("=" * 60)

    confirm = input("这将同步所有符合条件的技能，可能需要较长时间。是否继续？(y/N): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    try:
        async with async_db_session() as db:
            result = await clawhub_sync_service.sync_from_clawhub(db)

            print(f"\n同步结果:")
            print(f"  成功: {result.get('synced', 0)}")
            print(f"  失败: {result.get('failed', 0)}")

            if result.get('errors'):
                print(f"\n错误列表:")
                for error in result['errors']:
                    print(f"  - {error}")

    except Exception as e:
        print(f"❌ 完整同步失败: {e}")
        import traceback
        traceback.print_exc()

    print()


async def main():
    print("\n🔍 ClawHub Sync Service Test\n")

    # Test 1: Fetch skills
    await test_fetch_skills()

    # Test 2: Filter skills
    await test_filter_skills()

    # Test 3: Sync limited skills (first 5)
    await test_sync_limited()

    # Test 4: Full sync (optional, commented out by default)
    # await test_full_sync()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
