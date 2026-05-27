#!/usr/bin/env python3
"""
测试技能图标上传功能

测试内容：
1. 检查现有技能的图标URL
2. 触发 GitHub 技能同步
3. 验证图标是否上传到真实的 S3
4. 检查更新后的图标URL
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from sqlalchemy import select, func
from backend.database.db import async_db_session
from backend.app.marketplace.model.marketplace_skill import MarketplaceSkill
from backend.app.marketplace.service.github_sync_service import github_sync_service
from backend.common.log import log


async def check_skill_icons(db, title: str):
    """检查技能图标URL"""
    print("\n" + "="*80)
    print(f"📊 {title}")
    print("="*80)

    # 统计图标状态
    stmt = select(func.count()).select_from(MarketplaceSkill)
    total = (await db.execute(stmt)).scalar()
    print(f"\n✓ 技能总数: {total}")

    # 统计有图标的技能
    stmt = select(func.count()).select_from(MarketplaceSkill).where(
        MarketplaceSkill.icon_url.isnot(None)
    )
    with_icon = (await db.execute(stmt)).scalar()
    print(f"✓ 有图标的技能: {with_icon}")

    # 统计假CDN URL
    stmt = select(func.count()).select_from(MarketplaceSkill).where(
        MarketplaceSkill.icon_url.like('https://cdn.huanxing.ai/%')
    )
    fake_cdn = (await db.execute(stmt)).scalar()
    print(f"⚠️  假CDN URL: {fake_cdn}")

    # 统计真实S3 URL
    stmt = select(func.count()).select_from(MarketplaceSkill).where(
        MarketplaceSkill.icon_url.like('http://hasn-cdn.dcfuture.cn/%')
    )
    real_s3 = (await db.execute(stmt)).scalar()
    print(f"✓ 真实S3 URL: {real_s3}")

    # 查询前10个技能的图标URL
    stmt = select(
        MarketplaceSkill.skill_id,
        MarketplaceSkill.name_zh,
        MarketplaceSkill.icon_url
    ).limit(10)
    results = (await db.execute(stmt)).all()

    print("\n前10个技能的图标URL:")
    for skill_id, name_zh, icon_url in results:
        status = "✓" if icon_url and icon_url.startswith('http://hasn-cdn.dcfuture.cn/') else "⚠️"
        print(f"  {status} {skill_id}: {name_zh}")
        print(f"     {icon_url or 'None'}")


async def test_github_skill_sync(db):
    """测试 GitHub 技能同步"""
    print("\n" + "="*80)
    print("🔄 测试 GitHub 技能同步（图标上传）")
    print("="*80)

    try:
        result = await github_sync_service.sync_from_github(db, force=True)

        if result.get('success'):
            print(f"\n✅ 同步成功!")
            print(f"  - 同步数量: {result.get('synced', 0)}")
            print(f"  - 失败数量: {result.get('failed', 0)}")

            if result.get('errors'):
                print("\n错误信息:")
                for error in result['errors'][:5]:  # 只显示前5个错误
                    print(f"  - {error}")
        else:
            print(f"\n❌ 同步失败: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n❌ 同步异常: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def main():
    """主测试函数"""
    print("="*80)
    print("🧪 技能图标上传测试")
    print("="*80)

    async with async_db_session() as db:
        # 检查同步前的图标状态
        await check_skill_icons(db, "同步前的图标状态")

        # 测试同步
        sync_ok = await test_github_skill_sync(db)

        if sync_ok:
            # 提交事务
            await db.commit()

            # 检查同步后的图标状态
            await check_skill_icons(db, "同步后的图标状态")

    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(main())
