import asyncio
import asyncpg
from backend.core.conf import settings

async def check_table():
    conn = await asyncpg.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=settings.DATABASE_SCHEMA,
    )
    
    result = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'app_permission_grants'
        ORDER BY ordinal_position
    """)
    
    print("app_permission_grants 表结构:")
    for row in result:
        print(f"  {row['column_name']}: {row['data_type']} {'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'}")
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(check_table())
