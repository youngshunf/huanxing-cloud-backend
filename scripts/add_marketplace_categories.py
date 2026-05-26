#!/usr/bin/env python3
"""
补充技能市场分类
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.database.db import async_engine


async def add_missing_categories():
    """添加缺失的分类"""

    # 需要添加的分类
    new_categories = [
        {
            'slug': 'creativity',
            'name': '创意设计',
            'icon': '🎨',
            'sort_order': 7
        },
        {
            'slug': 'data',
            'name': '数据处理',
            'icon': '📈',
            'sort_order': 8
        },
        {
            'slug': 'entertainment',
            'name': '娱乐休闲',
            'icon': '🎮',
            'sort_order': 9
        },
        {
            'slug': 'other',
            'name': '其他',
            'icon': '📦',
            'sort_order': 99
        }
    ]

    async with async_engine.begin() as conn:
        for category in new_categories:
            # 检查是否已存在
            result = await conn.execute(
                text("SELECT id FROM marketplace_category WHERE slug = :slug"),
                {'slug': category['slug']}
            )
            existing = result.fetchone()

            if existing:
                print(f"⏭️  分类已存在: {category['slug']} - {category['name']}")
            else:
                # 插入新分类
                await conn.execute(
                    text("""
                        INSERT INTO marketplace_category (slug, name, icon, parent_slug, sort_order, created_time, updated_time)
                        VALUES (:slug, :name, :icon, NULL, :sort_order, NOW(), NOW())
                    """),
                    category
                )
                print(f"✅ 添加分类: {category['slug']} - {category['name']}")


async def list_all_categories():
    """列出所有分类"""
    async with async_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT id, slug, name, icon, sort_order FROM marketplace_category ORDER BY sort_order")
        )
        rows = result.fetchall()

        print(f"\n所有分类 ({len(rows)} 个):")
        print("-" * 60)
        for row in rows:
            print(f"  {row[1]:20s} {row[2]:15s} {row[3]:5s} (sort: {row[4]})")


async def main():
    print("=" * 60)
    print("补充技能市场分类")
    print("=" * 60)
    print()

    # 添加缺失的分类
    await add_missing_categories()

    # 列出所有分类
    await list_all_categories()

    print()
    print("=" * 60)
    print("完成")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
