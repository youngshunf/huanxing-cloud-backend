#!/usr/bin/env python3
"""
Recreate marketplace tables with new schema (multi-language support)
"""
import asyncio
from sqlalchemy import text
from backend.database.db import async_engine

async def recreate_tables():
    async with async_engine.begin() as conn:
        print("Dropping old marketplace tables...")
        await conn.execute(text("DROP TABLE IF EXISTS marketplace_download_history CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS marketplace_sync_log CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS marketplace_skill_version CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS marketplace_skill CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS marketplace_category CASCADE"))
        print("✓ Old tables dropped")

        print("\nCreating new tables...")

        # Read and execute SQL files using run_sync to execute raw SQL
        sql_files = [
            'backend/sql/marketplace_category.sql',
            'backend/sql/marketplace_skill.sql',
            'backend/sql/marketplace_skill_version.sql',
            'backend/sql/marketplace_sync_log.sql',
            'backend/sql/marketplace_download_history.sql',
        ]

        for sql_file in sql_files:
            print(f"  Executing {sql_file}...")
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()

                # Use run_sync to execute raw SQL with asyncpg
                def execute_raw_sql(sync_conn):
                    # Get the raw asyncpg connection
                    raw_conn = sync_conn.connection.driver_connection
                    # Execute the SQL file content
                    import asyncio
                    asyncio.get_event_loop().run_until_complete(
                        raw_conn.execute(sql_content)
                    )

                await conn.run_sync(execute_raw_sql)

        print("✓ All tables created successfully")

if __name__ == '__main__':
    asyncio.run(recreate_tables())
