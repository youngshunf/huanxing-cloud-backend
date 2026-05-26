#!/usr/bin/env python3
"""
Database migration script
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.database.db import async_engine


async def run_migration(sql_file: str):
    """Execute SQL migration file"""
    sql_path = Path(sql_file)
    if not sql_path.exists():
        print(f"❌ Migration file not found: {sql_file}")
        return False

    print(f"📄 Reading migration: {sql_path.name}")
    sql_content = sql_path.read_text(encoding='utf-8')

    print(f"🔄 Executing migration...")
    async with async_engine.begin() as conn:
        try:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            for i, stmt in enumerate(statements, 1):
                if stmt:
                    print(f"  [{i}/{len(statements)}] Executing statement...")
                    await conn.execute(text(stmt))

            print(f"✅ Migration completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False


async def main():
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]
    success = await run_migration(sql_file)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
