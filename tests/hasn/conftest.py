"""
HASN 测试基础设施 conftest

提供同步数据库 engine 和连接 fixtures，连接本地 PostgreSQL。
不依赖项目 .env 配置，直接使用硬编码的本地开发数据库地址。
"""

import pytest
from sqlalchemy import create_engine, text

# 本地开发数据库连接（PostgreSQL 127.0.0.1:15432，库名 huanxing，用户 mac）
# 如需修改，请直接编辑此常量
DATABASE_URL = 'postgresql+psycopg://mac@127.0.0.1:15432/huanxing'


@pytest.fixture(scope='module')
def db_engine():
    """创建同步 SQLAlchemy engine（整个测试模块共享一个连接池）"""
    engine = create_engine(DATABASE_URL, echo=False)
    yield engine
    engine.dispose()


@pytest.fixture(scope='function')
def db_conn(db_engine):
    """
    提供数据库连接，使用事务但不 commit（保持测试隔离）。
    测试结束后回滚，不影响数据库状态。
    """
    with db_engine.connect() as conn:
        trans = conn.begin()
        try:
            yield conn
        finally:
            trans.rollback()
