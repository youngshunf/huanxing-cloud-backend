#!/usr/bin/env python3
"""
Check database schema
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from backend.database.db import async_engine


async def check_table_schema(table_name: str):
    """Check if table exists and show its columns"""
    async with async_engine.connect() as conn:
        # Check if table exists
        result = await conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = '{table_name}'
            );
        """))
        exists = result.scalar()

        if not exists:
            print(f"❌ Table '{table_name}' does not exist")
            return

        print(f"✅ Table '{table_name}' exists")

        # Get columns
        result = await conn.execute(text(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = '{table_name}'
            ORDER BY ordinal_position;
        """))

        columns = result.fetchall()
        print(f"   Columns ({len(columns)}):")
        for col in columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"   - {col[0]}: {col[1]} {nullable}")


async def main():
    tables = [
        'marketplace_skill',
        'marketplace_skill_version',
        'marketplace_template',
        'marketplace_template_version',
        'marketplace_download',
        'marketplace_category',
    ]

    print("🔍 Checking database schema...\n")
    for table in tables:
        await check_table_schema(table)
        print()


if __name__ == '__main__':
    asyncio.run(main())
