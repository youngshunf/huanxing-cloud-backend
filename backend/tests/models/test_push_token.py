"""B3 - push_tokens model + migration 契约测试.

测试策略 (与 B2 `test_logout.py` 一致: 不依赖真实 Postgres / pytest-asyncio):
- 构造独立 SQLAlchemy metadata + in-memory SQLite 引擎 (sync), 手工建镜像表。
- 对 `PushChannel` / `PUSH_CHANNEL_VALUES` 做枚举契约断言 (M1 只有 'umeng_push')。
- 对 `PushToken` ORM 做字段 / 唯一约束存在性断言 (对齐 alembic 迁移契约)。
- 对 alembic 迁移模块 `20260421_b3_create_push_tokens.py` 做 revision 链断言
  (down_revision = B2; upgrade / downgrade 可执行)。

覆盖 B3 acceptance:
1. PushChannel enum 只含 'umeng_push' (M1 固定)
2. PushToken model 含 hasn_id / device_id / channel / token / registered_at / last_seen_at
3. push_tokens 表在 SQLite 上 CREATE + INSERT + 违反复合唯一 → IntegrityError
4. alembic 迁移 revision id / down_revision 正确 (chain 到 B2)
"""
from __future__ import annotations

import importlib

import pytest
import sqlalchemy as sa

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from backend.app.models.push_token import (
    PUSH_CHANNEL_VALUES,
    PushChannel,
    PushToken,
)

# ---------------------------------------------------------------------------
# 1. PushChannel 枚举契约
# ---------------------------------------------------------------------------


def test_push_channel_enum_only_contains_umeng_push() -> None:
    """M1 channel 枚举只能有 'umeng_push'; FCM / getui / jpush 等必须等到 M2.

    这是 PRD B3 的明确验收: 'PushChannel enum 只含 umeng_push 一个值（M1）'。
    """
    values = {c.value for c in PushChannel}
    assert values == {'umeng_push'}, (
        f'M1 PushChannel 必须仅含 umeng_push, 实际={values}. '
        f'若要加 FCM / 其他通道, 必须新开 M2 phase 评审 + 迁移。'
    )
    assert frozenset({'umeng_push'}) == PUSH_CHANNEL_VALUES


def test_push_channel_is_string_enum_for_db_storage() -> None:
    """channel 必须是 str 枚举 (DB 存字符串, 不存整数), 方便 alembic 与聚合服务对齐."""
    assert isinstance(PushChannel.UMENG_PUSH.value, str)
    assert PushChannel.UMENG_PUSH.value == 'umeng_push'


# ---------------------------------------------------------------------------
# 2. PushToken ORM 字段契约
# ---------------------------------------------------------------------------


def test_push_token_model_has_required_columns() -> None:
    """对齐 docs/架构设计/移动端/04 §5.3 + PRD B3 description."""
    table = PushToken.__table__
    col_names = {c.name for c in table.columns}

    required = {
        'id',
        'hasn_id',
        'device_id',
        'channel',
        'token',
        'registered_at',
        'last_seen_at',
    }
    missing = required - col_names
    assert not missing, f'push_tokens 缺字段: {missing}'


def test_push_token_table_has_composite_unique_constraint() -> None:
    """B3 核心约束: (hasn_id, device_id, channel) 复合唯一."""
    constraints = PushToken.__table__.constraints
    uniques = [c for c in constraints if isinstance(c, sa.UniqueConstraint)]
    assert uniques, 'PushToken 必须至少有 1 个 UniqueConstraint'

    cols_per_uq = [
        sorted(col.name for col in uq.columns) for uq in uniques
    ]
    expected = sorted(['hasn_id', 'device_id', 'channel'])
    assert expected in cols_per_uq, (
        f'(hasn_id, device_id, channel) 复合唯一约束缺失; 实际={cols_per_uq}'
    )


def test_push_token_table_has_hasn_id_index() -> None:
    """hasn_id 必须有独立索引 (按 owner 查活跃 token 是推送热路径)."""
    index_cols = [
        sorted(col.name for col in ix.columns)
        for ix in PushToken.__table__.indexes
    ]
    assert ['hasn_id'] in index_cols, f'hasn_id 索引缺失; 实际={index_cols}'


# ---------------------------------------------------------------------------
# 3. SQLite 端到端: CREATE + INSERT + 唯一冲突
# ---------------------------------------------------------------------------


class _IsolatedBase(DeclarativeBase):
    """孤立 declarative base, 避免污染生产 metadata."""


class _PushTokenMirror(_IsolatedBase):
    """与 PushToken 字段对齐的 SQLite 友好镜像.

    生产 Base 带 dataclass + TimeZone TypeDecorator, 直接在 SQLite 上跑会
    引入无关耦合; 此镜像只测"复合唯一索引是否生效"这一 DDL 语义契约。
    """

    __tablename__ = 'push_tokens'
    __table_args__ = (
        sa.UniqueConstraint(
            'hasn_id', 'device_id', 'channel',
            name='uq_push_tokens_hasn_device_channel',
        ),
    )

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    hasn_id: Mapped[str] = mapped_column(sa.String(40), nullable=False)
    device_id: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    channel: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, default='umeng_push'
    )
    token: Mapped[str] = mapped_column(sa.String(512), nullable=False, default='')


@pytest.fixture
def sqlite_session() -> sa.orm.Session:
    engine = sa.create_engine('sqlite://')
    _IsolatedBase.metadata.create_all(engine)
    session_factory = sa.orm.sessionmaker(engine, expire_on_commit=False)
    session = session_factory()
    yield session
    session.close()
    engine.dispose()


def test_push_token_insert_then_duplicate_triggers_unique_violation(sqlite_session: sa.orm.Session) -> None:
    """同一 (hasn_id, device_id, channel) 插两次 → 第二次 IntegrityError."""
    sqlite_session.add(
        _PushTokenMirror(
            hasn_id='h_test_001',
            device_id='device-aaa',
            channel='umeng_push',
            token='first-token',
        )
    )
    sqlite_session.commit()

    sqlite_session.add(
        _PushTokenMirror(
            hasn_id='h_test_001',
            device_id='device-aaa',
            channel='umeng_push',
            token='second-token-should-collide',
        )
    )
    with pytest.raises(IntegrityError):
        sqlite_session.commit()
    sqlite_session.rollback()


def test_push_token_different_device_allowed_for_same_hasn(sqlite_session: sa.orm.Session) -> None:
    """同一 hasn_id 下不同 device_id → 允许 (一个用户多设备)."""
    sqlite_session.add_all(
        [
            _PushTokenMirror(
                hasn_id='h_test_001',
                device_id='device-aaa',
                channel='umeng_push',
                token='tok-a',
            ),
            _PushTokenMirror(
                hasn_id='h_test_001',
                device_id='device-bbb',
                channel='umeng_push',
                token='tok-b',
            ),
        ]
    )
    sqlite_session.commit()

    count = sqlite_session.scalar(
        sa.select(sa.func.count()).select_from(_PushTokenMirror)
    )
    assert count == 2


# ---------------------------------------------------------------------------
# 4. Alembic 迁移模块契约
# ---------------------------------------------------------------------------


def test_b3_migration_module_chain() -> None:
    """B3 迁移 revision 链到 B2, upgrade/downgrade 可调用."""
    mod = importlib.import_module(
        'backend.alembic.versions.20260421_b3_create_push_tokens'
    )
    assert mod.revision == '20260421_b3_push_tokens'
    assert mod.down_revision == '20260421_b2_jwt_revoc', (
        'B3 必须 chain 在 B2 后面, 否则 alembic upgrade head 会丢新表'
    )
    assert callable(mod.upgrade)
    assert callable(mod.downgrade)
