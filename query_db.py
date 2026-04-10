import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys

async def main():
    engine = create_async_engine("postgresql+asyncpg://huanxing:HuanXing\!001@127.0.0.1:5432/huanxing")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT from_id, to_id, content, created_time FROM hasn_messages ORDER BY created_time DESC LIMIT 5;"))
        for row in result.fetchall():
            print(f"{row.created_time} {row.from_id} -> {row.to_id}: {row.content}")

asyncio.run(main())
