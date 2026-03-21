"""
HASN 数据库结构验证测试桩

所有测试均标记为 skip（表尚未创建）。
Plan 01 Wave 3 完成数据库迁移后，解除 skip 标记并执行验证。

测试覆盖范围：
- DB-01: hasn_clients 表（存在性、字段、索引、唯一约束）
- DB-02: hasn_agents 表（新增字段、外键、唯一约束）
- DB-03: 旧 hasn_agents 表（VARCHAR 主键）已清除
"""

import pytest
from sqlalchemy import text


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_clients_table_exists(db_conn):
    """DB-01: hasn_clients 表存在"""
    result = db_conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='hasn_clients')"
    ))
    assert result.scalar() is True


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_clients_columns(db_conn):
    """DB-01: hasn_clients 表包含所有必要字段"""
    result = db_conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='hasn_clients' ORDER BY ordinal_position"
    ))
    columns = [row[0] for row in result]
    for col in ['id', 'client_id', 'user_hasn_id', 'client_type', 'device_name', 'device_info', 'last_seen_at', 'status', 'created_time', 'updated_time']:
        assert col in columns, f'缺少字段: {col}'


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_clients_unique_constraint(db_conn):
    """DB-01: client_id 有唯一约束"""
    result = db_conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_name='hasn_clients' AND constraint_type='UNIQUE'"
    ))
    assert result.scalar() >= 1


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_clients_indexes(db_conn):
    """DB-01: hasn_clients 有 user_hasn_id 和 status 索引"""
    result = db_conn.execute(text(
        "SELECT indexname FROM pg_indexes WHERE tablename='hasn_clients'"
    ))
    index_names = [row[0] for row in result]
    assert 'idx_hasn_clients_user' in index_names
    assert 'idx_hasn_clients_status' in index_names


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_clients_insert(db_conn):
    """DB-01: 可以插入测试行"""
    db_conn.execute(text(
        "INSERT INTO hasn_clients (client_id, user_hasn_id, client_type, device_name) VALUES ('c_test_001', 'h_test_001', 'desktop', '测试设备') ON CONFLICT (client_id) DO NOTHING"
    ))
    result = db_conn.execute(text("SELECT client_id FROM hasn_clients WHERE client_id = 'c_test_001'"))
    assert result.scalar() == 'c_test_001'
    db_conn.execute(text("DELETE FROM hasn_clients WHERE client_id = 'c_test_001'"))


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_agents_table_exists(db_conn):
    """DB-02: hasn_agents 表存在"""
    result = db_conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='hasn_agents')"
    ))
    assert result.scalar() is True


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_agents_new_fields(db_conn):
    """DB-02: hasn_agents 包含 type/server_id/home_client_id/created_via 字段"""
    result = db_conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='hasn_agents'"
    ))
    columns = [row[0] for row in result]
    for col in ['type', 'server_id', 'home_client_id', 'created_via']:
        assert col in columns, f'缺少新增字段: {col}'


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_agents_all_columns(db_conn):
    """DB-02: hasn_agents 包含全部字段"""
    result = db_conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='hasn_agents' ORDER BY ordinal_position"
    ))
    columns = [row[0] for row in result]
    for col in ['id', 'hasn_id', 'star_id', 'owner_id', 'name', 'agent_name', 'type', 'server_id', 'home_client_id', 'api_key_hash', 'status', 'created_via', 'created_time', 'updated_time']:
        assert col in columns, f'缺少字段: {col}'


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_agents_foreign_key(db_conn):
    """DB-02: home_client_id 外键引用 hasn_clients(id)"""
    result = db_conn.execute(text("""
        SELECT tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'hasn_agents'
          AND tc.constraint_type = 'FOREIGN KEY'
          AND kcu.column_name = 'home_client_id'
    """))
    assert result.scalar() is not None, '缺少 home_client_id 外键'


@pytest.mark.skip(reason='表尚未创建')
def test_hasn_agents_unique_constraints(db_conn):
    """DB-02: hasn_id 和 star_id 有唯一约束"""
    result = db_conn.execute(text("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = 'hasn_agents' AND tc.constraint_type = 'UNIQUE'
    """))
    unique_columns = [row[0] for row in result]
    assert 'hasn_id' in unique_columns, '缺少 hasn_id 唯一约束'
    assert 'star_id' in unique_columns, '缺少 star_id 唯一约束'


@pytest.mark.skip(reason='旧表不存在或已 DROP')
def test_hasn_agents_old_table_dropped(db_conn):
    """DB-03: 旧 hasn_agents 表已清除（VARCHAR 主键版本不存在）"""
    # 验证 hasn_agents 的 id 列类型是 bigint 而不是 varchar
    result = db_conn.execute(text(
        "SELECT data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='hasn_agents' AND column_name='id'"
    ))
    data_type = result.scalar()
    assert data_type == 'bigint', f'id 类型应为 bigint，实际为 {data_type}（旧表未清除？）'
