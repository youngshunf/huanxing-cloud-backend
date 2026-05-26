#!/usr/bin/env python3
"""
Check test data
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.database.db import async_engine


async def check_data():
    """Check test data"""
    async with async_engine.connect() as conn:
        print("🔍 Checking marketplace_skill data...\n")

        result = await conn.execute(text("""
            SELECT skill_id, namespace, slug, name_en, name_zh,
                   description_en, description_zh, is_private
            FROM marketplace_skill
            LIMIT 5;
        """))

        rows = result.fetchall()
        if not rows:
            print("❌ No data found in marketplace_skill table")
            return

        print(f"✅ Found {len(rows)} skills:\n")
        for row in rows:
            print(f"Skill ID: {row[0]}")
            print(f"  Namespace: {row[1]}")
            print(f"  Slug: {row[2]}")
            print(f"  Name EN: {row[3]}")
            print(f"  Name ZH: {row[4]}")
            print(f"  Desc EN: {row[5][:50] if row[5] else None}...")
            print(f"  Desc ZH: {row[6][:50] if row[6] else None}...")
            print(f"  Is Private: {row[7]}")
            print()


if __name__ == '__main__':
    asyncio.run(check_data())
