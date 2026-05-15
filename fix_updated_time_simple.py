import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from backend.database.db import create_database_url

async def main():
    db_url = create_database_url(unittest=False)
    engine = create_async_engine(db_url, echo=False, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        # 获取所有 app_* 表
        result = await conn.execute(text("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename LIKE 'app_%'
        """))
        tables = [row[0] for row in result]

        for table in tables:
            try:
                await conn.execute(text(f'ALTER TABLE {table} ALTER COLUMN updated_time DROP NOT NULL'))
                print(f'✓ {table}')
            except Exception as e:
                print(f'✗ {table}: {e}')

    await engine.dispose()

asyncio.run(main())
