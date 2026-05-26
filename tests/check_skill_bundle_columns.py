import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=15432,
        user='postgres',
        password='123456',
        database='huanxing'
    )
    columns = await conn.fetch("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'hasn_skill_bundle'
        AND column_name LIKE '%time%'
        ORDER BY ordinal_position
    """)
    print('hasn_skill_bundle 时间戳字段:')
    for col in columns:
        print(f'  {col["column_name"]}')
    await conn.close()

asyncio.run(check())
