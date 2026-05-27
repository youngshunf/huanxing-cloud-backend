#!/usr/bin/env python3
"""
测试模板同步和下载功能

测试内容：
1. GitHub App 模板同步
2. 模板打包服务
3. 模板下载 API
4. 检查数据库中的模板数据
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from sqlalchemy import select, func
from backend.database.db import async_db_session
from backend.app.marketplace.model.marketplace_template import MarketplaceTemplate
from backend.app.marketplace.model.marketplace_template_version import MarketplaceTemplateVersion
from backend.app.marketplace.service.github_app_sync_service import github_app_sync_service
from backend.app.marketplace.service.app_package_service import app_package_service
from backend.common.log import log


async def check_template_data(db):
    """检查数据库中的模板数据"""
    print("\n" + "="*80)
    print("📊 检查数据库中的模板数据")
    print("="*80)

    # 统计模板总数
    stmt = select(func.count()).select_from(MarketplaceTemplate)
    total = (await db.execute(stmt)).scalar()
    print(f"\n✓ 模板总数: {total}")

    # 按类型统计
    stmt = select(
        MarketplaceTemplate.template_type,
        func.count()
    ).group_by(MarketplaceTemplate.template_type)

    results = (await db.execute(stmt)).all()
    print("\n按类型统计:")
    for template_type, count in results:
        print(f"  - {template_type}: {count}")

    # 查询最近的模板
    stmt = select(MarketplaceTemplate).order_by(
        MarketplaceTemplate.synced_at.desc()
    ).limit(5)

    templates = (await db.execute(stmt)).scalars().all()

    if templates:
        print("\n最近同步的模板:")
        for t in templates:
            print(f"  - {t.template_id}: {t.name}")
            print(f"    类型: {t.template_type}")
            print(f"    同步时间: {t.synced_at}")

    # 检查版本数据
    stmt = select(func.count()).select_from(MarketplaceTemplateVersion)
    version_count = (await db.execute(stmt)).scalar()
    print(f"\n✓ 模板版本总数: {version_count}")

    # 查询最新版本
    stmt = select(MarketplaceTemplateVersion).where(
        MarketplaceTemplateVersion.is_latest == True
    ).limit(5)

    versions = (await db.execute(stmt)).scalars().all()

    if versions:
        print("\n最新版本:")
        for v in versions:
            print(f"  - {v.template_id} v{v.version}")
            print(f"    包URL: {v.package_url}" if hasattr(v, 'package_url') else f"    包路径: {getattr(v, 'package_path', 'N/A')}")
            print(f"    文件大小: {v.file_size / 1024:.1f} KB" if v.file_size else "    文件大小: N/A")
            print(f"    文件哈希: {v.file_hash[:16]}..." if v.file_hash else "    文件哈希: N/A")


async def test_github_app_sync(db):
    """测试 GitHub App 模板同步"""
    print("\n" + "="*80)
    print("🔄 测试 GitHub App 模板同步")
    print("="*80)

    try:
        result = await github_app_sync_service.sync_from_github(db, force=True)

        if result.get('success'):
            print(f"\n✅ 同步成功!")
            print(f"  - 同步数量: {result.get('synced', 0)}")
            print(f"  - 失败数量: {result.get('failed', 0)}")

            if result.get('errors'):
                print("\n错误信息:")
                for error in result['errors']:
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


async def test_package_service():
    """测试模板打包服务"""
    print("\n" + "="*80)
    print("📦 测试模板打包服务")
    print("="*80)

    # 测试打包一个模板
    test_app_id = "assistant"  # 使用默认的 assistant 模板
    test_version = "1.0.0"

    try:
        print(f"\n正在打包模板: {test_app_id} v{test_version}")

        package_info = await app_package_service.build_app_package(
            test_app_id,
            test_version
        )

        print(f"\n✅ 打包成功!")
        print(f"  - 包路径: {package_info['package_path']}")
        print(f"  - 文件大小: {package_info['file_size'] / 1024:.1f} KB")
        print(f"  - 文件哈希: {package_info['file_hash'][:16]}...")

        # 验证文件存在
        package_path = Path(package_info['package_path'])
        if package_path.exists():
            print(f"\n✓ 包文件存在: {package_path}")
        else:
            print(f"\n✗ 包文件不存在: {package_path}")
            return False

    except FileNotFoundError as e:
        print(f"\n⚠️  模板目录不存在: {e}")
        print("这是正常的，如果 huanxing-hub 仓库中没有 templates/ 目录")
        return True  # 不算失败
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_cache_operations():
    """测试缓存操作"""
    print("\n" + "="*80)
    print("🗄️  测试缓存操作")
    print("="*80)

    try:
        # 测试获取缓存
        test_app_id = "assistant"
        test_version = "1.0.0"

        cached = await app_package_service.get_cached_package(test_app_id, test_version)

        if cached:
            print(f"\n✓ 找到缓存包:")
            print(f"  - 路径: {cached['package_path']}")
            print(f"  - 大小: {cached['file_size'] / 1024:.1f} KB")
        else:
            print(f"\n✓ 没有缓存（这是正常的）")

        # 测试清理旧包
        print(f"\n清理旧包...")
        await app_package_service.cleanup_old_packages(keep_versions=3)
        print(f"✓ 清理完成")

    except Exception as e:
        print(f"\n❌ 缓存操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def check_huanxing_hub_repo():
    """检查 huanxing-hub 仓库状态"""
    print("\n" + "="*80)
    print("📁 检查 huanxing-hub 仓库")
    print("="*80)

    from backend.core.conf import settings

    hub_path = Path(getattr(settings, 'HUANXING_HUB_LOCAL_PATH', '/tmp/huanxing-hub'))

    print(f"\n仓库路径: {hub_path}")

    if not hub_path.exists():
        print(f"⚠️  仓库不存在")
        print(f"需要先克隆仓库:")
        print(f"  git clone https://github.com/youngshunf/huanxing-hub.git {hub_path}")
        return False

    print(f"✓ 仓库存在")

    # 检查 templates 目录
    templates_dir = hub_path / 'templates'
    if templates_dir.exists():
        print(f"✓ templates/ 目录存在")

        # 统计模板数量
        template_count = sum(1 for d in templates_dir.iterdir()
                           if d.is_dir() and not d.name.startswith('_'))
        print(f"  - 模板数量: {template_count}")

        # 列出前 5 个模板
        templates = [d.name for d in templates_dir.iterdir()
                    if d.is_dir() and not d.name.startswith('_')][:5]
        if templates:
            print(f"  - 示例模板: {', '.join(templates)}")
    else:
        print(f"⚠️  templates/ 目录不存在")
        return False

    # 检查 skills 目录
    skills_dir = hub_path / 'skills'
    if skills_dir.exists():
        print(f"✓ skills/ 目录存在")

        # 统计技能数量
        skill_count = sum(1 for root, dirs, files in skills_dir.walk()
                         if 'manifest.yaml' in files)
        print(f"  - 技能数量: {skill_count}")
    else:
        print(f"⚠️  skills/ 目录不存在")

    return True


async def main():
    """主测试函数"""
    print("="*80)
    print("🧪 模板同步和下载功能测试")
    print("="*80)

    # 检查仓库
    repo_ok = await check_huanxing_hub_repo()

    async with async_db_session() as db:
        # 检查现有数据
        await check_template_data(db)

        # 如果仓库存在，测试同步
        if repo_ok:
            sync_ok = await test_github_app_sync(db)

            if sync_ok:
                # 提交事务
                await db.commit()

                # 同步后再次检查数据
                await check_template_data(db)
        else:
            print("\n⚠️  跳过同步测试（仓库不存在）")

    # 测试打包服务
    await test_package_service()

    # 测试缓存操作
    await test_cache_operations()

    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(main())
