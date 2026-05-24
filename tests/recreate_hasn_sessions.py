#!/usr/bin/env python3
"""重新创建 hasn_sessions 表"""

import asyncio
import asyncpg


async def recreate_table():
    # 连接数据库
    conn = await asyncpg.connect(
        host='127.0.0.1',
        port=15432,
        user='postgres',
        password='123456',
        database='huanxing'
    )

    try:
        # 删除旧表
        print("删除旧表...")
        await conn.execute('DROP TABLE IF EXISTS hasn_sessions CASCADE')

        # 创建新表
        print("创建新表...")
        with open('backend/sql/hasn/hasn_sessions.sql', 'r') as f:
            sql = f.read()

        await conn.execute(sql)

        print("✅ hasn_sessions 表重新创建成功")

        # 验证表结构
        columns = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'hasn_sessions'
            ORDER BY ordinal_position
        """)

        print("\n表结构:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']}", end='')
            if col['character_maximum_length']:
                print(f"({col['character_maximum_length']})")
            else:
                print()

    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(recreate_table())
