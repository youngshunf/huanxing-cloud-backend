"""重新创建 hasn_task 表"""
import asyncio
import asyncpg

async def recreate_table():
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=15432,
        user='postgres',
        password='123456',
        database='huanxing'
    )

    try:
        # 删除旧表
        await conn.execute('DROP TABLE IF EXISTS hasn_task CASCADE;')
        print("✓ 删除旧表成功")

        # 读取并执行 SQL 文件
        with open('backend/sql/hasn/hasn_task.sql', 'r', encoding='utf-8') as f:
            sql = f.read()

        await conn.execute(sql)
        print("✓ 创建新表成功")

        # 验证表结构
        columns = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'hasn_task'
            ORDER BY ordinal_position;
        """)

        print("\n表结构:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']}")

    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(recreate_table())
