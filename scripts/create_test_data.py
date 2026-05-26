#!/usr/bin/env python3
"""
Create test data for marketplace
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.database.db import async_engine


async def create_test_data():
    """Create test data for marketplace"""
    async with async_engine.begin() as conn:
        print("🔄 Creating test data...")

        # 1. Create categories
        print("\n1️⃣ Creating categories...")
        await conn.execute(text("""
            INSERT INTO marketplace_category (slug, name, icon, parent_slug, sort_order, created_time)
            VALUES
                ('productivity', '生产力工具', '⚡', NULL, 1, NOW()),
                ('communication', '沟通协作', '💬', NULL, 2, NOW()),
                ('development', '开发工具', '🛠️', NULL, 3, NOW()),
                ('ai-assistant', 'AI 助手', '🤖', NULL, 4, NOW())
            ON CONFLICT (slug) DO NOTHING;
        """))
        print("   ✅ Categories created")

        # 2. Create skills
        print("\n2️⃣ Creating skills...")
        await conn.execute(text("""
            INSERT INTO marketplace_skill (
                skill_id, namespace, slug,
                name_en, name_zh,
                description_en, description_zh,
                source_language,
                icon_url, emoji,
                author_id, author_name,
                category, tags,
                pricing_type, price,
                is_private, is_official,
                download_count, star_count,
                source_type, source_repo_url,
                created_time, updated_time
            )
            VALUES
                (
                    'huanxing/translator-pro', 'huanxing', 'translator-pro',
                    'Translator Pro', '专业翻译助手',
                    'Professional translation tool with multi-language support',
                    '支持多语言的专业翻译工具',
                    'zh',
                    NULL, '🌐',
                    1, 'HuanXing Team',
                    'productivity', 'translation,language,ai',
                    'free', 0,
                    false, true,
                    1250, 89,
                    'github', 'https://github.com/huanxing/translator-pro',
                    NOW(), NOW()
                ),
                (
                    'huanxing/code-reviewer', 'huanxing', 'code-reviewer',
                    'Code Reviewer', '代码审查助手',
                    'AI-powered code review assistant',
                    'AI 驱动的代码审查助手',
                    'en',
                    NULL, '🔍',
                    1, 'HuanXing Team',
                    'development', 'code,review,ai',
                    'free', 0,
                    false, true,
                    856, 67,
                    'github', 'https://github.com/huanxing/code-reviewer',
                    NOW(), NOW()
                ),
                (
                    'community/meeting-scheduler', 'community', 'meeting-scheduler',
                    'Meeting Scheduler', '会议安排助手',
                    'Smart meeting scheduling assistant',
                    '智能会议安排助手',
                    'zh',
                    NULL, '📅',
                    2, 'Community Dev',
                    'communication', 'meeting,schedule,calendar',
                    'free', 0,
                    false, false,
                    423, 34,
                    'github', 'https://github.com/community/meeting-scheduler',
                    NOW(), NOW()
                )
            ON CONFLICT (skill_id) DO NOTHING;
        """))
        print("   ✅ Skills created")

        # 3. Create skill versions
        print("\n3️⃣ Creating skill versions...")
        await conn.execute(text("""
            INSERT INTO marketplace_skill_version (
                skill_id, version, changelog,
                package_url, file_hash, file_size,
                is_latest, published_at, created_time
            )
            VALUES
                (
                    'huanxing/translator-pro', '1.0.0',
                    'Initial release with basic translation features',
                    'https://cdn.huanxing.com/skills/translator-pro-1.0.0.zip',
                    'abc123def456', 1024000,
                    true, NOW(), NOW()
                ),
                (
                    'huanxing/code-reviewer', '1.2.0',
                    'Added support for Python and JavaScript',
                    'https://cdn.huanxing.com/skills/code-reviewer-1.2.0.zip',
                    'def789ghi012', 2048000,
                    true, NOW(), NOW()
                ),
                (
                    'community/meeting-scheduler', '0.9.0',
                    'Beta release with calendar integration',
                    'https://cdn.huanxing.com/skills/meeting-scheduler-0.9.0.zip',
                    'ghi345jkl678', 512000,
                    true, NOW(), NOW()
                )
            ON CONFLICT (skill_id, version) DO NOTHING;
        """))
        print("   ✅ Skill versions created")

        # 4. Create templates
        print("\n4️⃣ Creating templates...")
        await conn.execute(text("""
            INSERT INTO marketplace_template (
                template_id, namespace, slug, template_type,
                name, name_en, name_zh,
                description, description_en, description_zh,
                source_language,
                icon_url, emoji,
                author_id, author_name,
                pricing_type, price,
                is_private, is_official,
                download_count,
                category, tags,
                source_type, source_repo_url,
                created_time
            )
            VALUES
                (
                    'huanxing/customer-service-bot', 'huanxing', 'customer-service-bot', 'agent',
                    'Customer Service Bot', 'Customer Service Bot', '客服机器人',
                    'AI customer service template', 'AI customer service template', 'AI 客服模板',
                    'zh',
                    NULL, '🤖',
                    1, 'HuanXing Team',
                    'free', 0,
                    false, true,
                    567,
                    'ai-assistant', 'customer-service,chatbot,ai',
                    'github', 'https://github.com/huanxing/customer-service-bot',
                    NOW()
                )
            ON CONFLICT (template_id) DO NOTHING;
        """))
        print("   ✅ Templates created")

        print("\n✅ Test data created successfully!")


async def main():
    try:
        await create_test_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
