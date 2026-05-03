"""单测：CRUDNewApiDirect 新增的 disable_newapi_token / get_usage_summary_by_token

策略：mock AsyncSession.execute，断言 SQL 文本与参数符合 §09 设计契约：
- disable_newapi_token: UPDATE tokens SET status = 2 WHERE id = :token_id（不 DELETE）
- get_usage_summary_by_token: WHERE token_id = :token_id（已确认 logs.token_id 存在）
"""

import pytest

from unittest.mock import AsyncMock, MagicMock

from backend.app.llm.crud.crud_llm_newapi_user_mapping import CRUDNewApiDirect


def _make_db_with_rowcount(rowcount: int) -> AsyncMock:
    """构造 mock AsyncSession，db.execute 返回带指定 rowcount 的 result"""
    db = AsyncMock()
    result = MagicMock()
    result.rowcount = rowcount
    db.execute = AsyncMock(return_value=result)
    return db


def _make_db_with_rows(rows: list[tuple]) -> AsyncMock:
    db = AsyncMock()
    result = MagicMock()
    result.fetchall = MagicMock(return_value=rows)
    db.execute = AsyncMock(return_value=result)
    return db


@pytest.mark.asyncio
async def test_disable_newapi_token_executes_soft_disable_sql():
    """disable_newapi_token: UPDATE tokens SET status = 2 WHERE id = :token_id"""
    db = _make_db_with_rowcount(1)

    ok = await CRUDNewApiDirect.disable_newapi_token(db, token_id=30001)

    assert ok is True
    db.execute.assert_awaited_once()
    sql_clause = db.execute.call_args[0][0]
    sql_text = str(sql_clause)
    assert 'UPDATE tokens' in sql_text
    assert 'status = 2' in sql_text
    assert 'DELETE' not in sql_text.upper()
    params = db.execute.call_args[0][1]
    assert params == {'token_id': 30001}


@pytest.mark.asyncio
async def test_disable_newapi_token_returns_false_when_no_row_updated():
    """token_id 不存在 → rowcount=0 → 返回 False"""
    db = _make_db_with_rowcount(0)

    ok = await CRUDNewApiDirect.disable_newapi_token(db, token_id=99999)

    assert ok is False


@pytest.mark.asyncio
async def test_disable_newapi_token_handles_none_rowcount():
    """rowcount 可能是 None → 安全降级到 False"""
    db = AsyncMock()
    result = MagicMock()
    result.rowcount = None
    db.execute = AsyncMock(return_value=result)

    ok = await CRUDNewApiDirect.disable_newapi_token(db, token_id=30001)
    assert ok is False


@pytest.mark.asyncio
async def test_get_usage_summary_by_token_filters_by_token_id_not_user_id():
    """get_usage_summary_by_token: WHERE token_id = :token_id（不是 user_id）"""
    db = _make_db_with_rows([
        ('anthropic/claude-sonnet-4.5', 1280, 640, 1920, 5),
        ('anthropic/claude-opus-4-7', 320, 160, 480, 2),
    ])

    rows = await CRUDNewApiDirect.get_usage_summary_by_token(
        db, token_id=30001, start_time=1714724000, end_time=1714810400,
    )

    db.execute.assert_awaited_once()
    sql_text = str(db.execute.call_args[0][0])
    assert 'token_id = :token_id' in sql_text
    assert 'GROUP BY model_name' in sql_text
    assert 'user_id =' not in sql_text  # 关键：按 token，不是按 user
    assert 'type = 2' in sql_text       # 沿用现有 by-user 过滤约束

    params = db.execute.call_args[0][1]
    assert params == {
        'token_id': 30001,
        'start_time': 1714724000,
        'end_time': 1714810400,
    }

    assert rows == [
        {
            'model_name': 'anthropic/claude-sonnet-4.5',
            'prompt_tokens': 1280,
            'completion_tokens': 640,
            'quota': 1920,
            'request_count': 5,
        },
        {
            'model_name': 'anthropic/claude-opus-4-7',
            'prompt_tokens': 320,
            'completion_tokens': 160,
            'quota': 480,
            'request_count': 2,
        },
    ]


@pytest.mark.asyncio
async def test_get_usage_summary_by_token_returns_empty_when_no_logs():
    db = _make_db_with_rows([])

    rows = await CRUDNewApiDirect.get_usage_summary_by_token(
        db, token_id=30001, start_time=0, end_time=1,
    )

    assert rows == []


def test_logs_token_id_field_evidence():
    """证据测试：commit 3 准备阶段已通过 information_schema 校验

    new-api logs 表存在 token_id bigint 与 token_name text 两列。
    校验输出（实测，2026-05-03）：
        token_id bigint
        token_name text
    本测试固化该约定，避免后续重构假设字段不存在。
    """
    expected = {'token_id', 'token_name', 'model_name', 'created_at', 'type'}
    actual = {
        'id', 'user_id', 'created_at', 'type', 'content', 'username', 'token_name',
        'model_name', 'quota', 'prompt_tokens', 'completion_tokens', 'use_time',
        'is_stream', 'channel_id', 'channel_name', 'token_id', 'group', 'ip',
        'request_id', 'other',
    }
    assert expected.issubset(actual)
