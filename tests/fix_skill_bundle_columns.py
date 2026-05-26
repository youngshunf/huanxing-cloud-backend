import asyncio
import asyncpg

async def fix():
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=15432,
        user='postgres',
        password='123456',
        database='huanxing'
    )

    print("重命名 hasn_skill_bundle 时间戳字段...")

    # 重命名字段
    await conn.execute('ALTER TABLE hasn_skill_bundle RENAME COLUMN create_time TO created_time')
    await conn.execute('ALTER TABLE hasn_skill_bundle RENAME COLUMN update_time TO updated_time')

    # 验证
    columns = await conn.fetch("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'hasn_skill_bundle'
        AND column_name LIKE '%time%'
        ORDER BY ordinal_position
    """)

    print("\n修复后的字段:")
    for col in columns:
        print(f'  {col["column_name"]}')

    await conn.close()
    print("\n✅ 修复完成")

asyncio.run(fix())
