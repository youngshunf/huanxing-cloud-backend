"""检查技能同步流程是否打通"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from backend.core.conf import settings

async def check_sync_flow():
    print("=" * 80)
    print("技能同步流程检查")
    print("=" * 80)

    # 创建数据库引擎
    engine = create_async_engine(
        f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_SCHEMA}",
        echo=False
    )

    async with AsyncSession(engine) as db:
        # 1. 检查三种来源的技能数量
        print("\n1. 检查技能来源分布:")
        print("-" * 80)

        from backend.app.marketplace.crud.crud_marketplace_skill import marketplace_skill_dao

        all_skills = await marketplace_skill_dao.get_all(db)

        clawhub_skills = [s for s in all_skills if s.skill_id.startswith('clawhub/')]
        github_skills = [s for s in all_skills if not s.skill_id.startswith('clawhub/') and not s.skill_id.startswith('huanxing/') and not s.skill_id.startswith('community/')]
        huanxing_skills = [s for s in all_skills if s.skill_id.startswith('huanxing/') or s.skill_id.startswith('community/')]

        print(f"  ClawHub 同步: {len(clawhub_skills)} 个")
        print(f"  GitHub 仓库 (skills/): {len(github_skills)} 个")
        print(f"  自己整理 (huanxing/community): {len(huanxing_skills)} 个")
        print(f"  总计: {len(all_skills)} 个")

        # 2. 检查同步服务
        print("\n2. 检查同步服务:")
        print("-" * 80)

        from backend.app.marketplace.service.clawhub_sync_service import clawhub_sync_service
        from backend.app.marketplace.service.github_sync_service import github_sync_service
        from backend.app.marketplace.service.github_app_sync_service import github_app_sync_service

        print(f"  ✓ ClawHub 同步服务: {clawhub_sync_service.__class__.__name__}")
        print(f"    - API URL: {clawhub_sync_service.clawhub_api_url}")
        print(f"    - 本地路径: {clawhub_sync_service.hub_local_path}")

        print(f"  ✓ GitHub 同步服务: {github_sync_service.__class__.__name__}")
        print(f"    - 仓库 URL: {github_sync_service.repo_url}")
        print(f"    - 本地路径: {github_sync_service.local_path}")

        print(f"  ✓ GitHub 应用同步服务: {github_app_sync_service.__class__.__name__}")

        # 3. 检查 webhook 配置
        print("\n3. 检查 Webhook 配置:")
        print("-" * 80)

        webhook_secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', None)
        if webhook_secret:
            print(f"  ✓ GitHub Webhook Secret: 已配置")
        else:
            print(f"  ⚠ GitHub Webhook Secret: 未配置（开发模式）")

        # 4. 检查同步日志
        print("\n4. 检查最近的同步记录:")
        print("-" * 80)

        from sqlalchemy import text

        logs = await db.execute(
            text("SELECT sync_type, status, items_synced, items_failed, started_at FROM marketplace_sync_log ORDER BY started_at DESC LIMIT 5")
        )

        for log in logs:
            print(f"  {log[0]:10} | {log[1]:10} | 成功: {log[2] or 0:3} | 失败: {log[3] or 0:3} | {log[4]}")

        # 5. 检查翻译状态
        print("\n5. 检查翻译状态:")
        print("-" * 80)

        translated = await db.execute(
            text("SELECT COUNT(*) FROM marketplace_skill WHERE name_en IS NOT NULL AND name_zh IS NOT NULL")
        )
        translated_count = translated.scalar()

        total = len(all_skills)
        percentage = (translated_count / total * 100) if total > 0 else 0

        print(f"  已翻译: {translated_count}/{total} ({percentage:.1f}%)")

        # 6. 检查 API 端点
        print("\n6. 检查 API 端点:")
        print("-" * 80)
        print(f"  管理端同步触发:")
        print(f"    POST /api/v1/marketplace/admin/sync/clawhub")
        print(f"    POST /api/v1/marketplace/admin/sync/github")
        print(f"    POST /api/v1/marketplace/admin/sync/github/apps")
        print(f"  Webhook 接收:")
        print(f"    POST /api/v1/marketplace/webhook/github/skills")
        print(f"    POST /api/v1/marketplace/webhook/github/apps")

        # 7. 总结
        print("\n" + "=" * 80)
        print("流程检查总结:")
        print("=" * 80)

        issues = []

        if len(clawhub_skills) == 0:
            issues.append("⚠ ClawHub 技能数量为 0，可能未同步")
        else:
            print(f"✓ ClawHub 同步: {len(clawhub_skills)} 个技能")

        if len(github_skills) == 0:
            issues.append("⚠ GitHub 技能数量为 0，可能未同步")
        else:
            print(f"✓ GitHub 同步: {len(github_skills)} 个技能")

        if percentage < 90:
            issues.append(f"⚠ 翻译覆盖率较低: {percentage:.1f}%")
        else:
            print(f"✓ 翻译覆盖率: {percentage:.1f}%")

        if not webhook_secret:
            issues.append("⚠ Webhook Secret 未配置")
        else:
            print(f"✓ Webhook 已配置")

        if issues:
            print("\n需要注意的问题:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✓ 所有检查通过！")

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(check_sync_flow())
