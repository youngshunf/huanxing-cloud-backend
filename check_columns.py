import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from backend.database.db import create_database_url

async def check():
    db_url = create_database_url(unittest=False)
    engine = create_async_engine(db_url, echo=False)
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'app_permission_grants'
            AND column_name IN ('created_time', 'updated_time', 'granted_at')
            ORDER BY column_name
        """))
        print("app_permission_grants columns:")
        for row in result:
            print(f'  {row[0]}: nullable={row[1]}')
    await engine.dispose()

asyncio.run(check())
