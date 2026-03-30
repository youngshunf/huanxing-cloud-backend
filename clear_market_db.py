import asyncio
import os
import sys

sys.path.append(os.path.abspath('.'))

from backend.database.db import async_db_session
from sqlalchemy import text

async def clear_db():
    try:
        async with async_db_session.begin() as db:
            await db.execute(text("DELETE FROM marketplace_app_version"))
            await db.execute(text("DELETE FROM marketplace_skill_version"))
            await db.execute(text("DELETE FROM marketplace_sop_version"))
            await db.execute(text("DELETE FROM marketplace_app"))
            await db.execute(text("DELETE FROM marketplace_skill"))
            await db.execute(text("DELETE FROM marketplace_sop"))
            print("Successfully cleared all marketplace tables.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    asyncio.run(clear_db())
