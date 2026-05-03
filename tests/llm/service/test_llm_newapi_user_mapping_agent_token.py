"""单测：LlmNewapiUserMappingService 的 Hermes Agent 级 LLM token 隔离方法（§09）

策略：mock newapi_direct_dao 的 staticmethod + ensure_newapi_user，
db / newapi_db 用 AsyncMock；不真连任何数据库，验证：
- ensure_agent_token: 首次签发 / 幂等 / 撤销后再签 / sha256 持久化
- 其他方法（revoke / rotate / usage_summary）由后续 commit 追加。
"""

import hashlib

import pytest

from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.hermes.model import HermesAgentLlmToken
from backend.app.llm.schema.llm_newapi_user_mapping import NewApiMappingInfo
from backend.app.llm.service.llm_newapi_user_mapping_service import LlmNewapiUserMappingService


# ---------- 共用 fixtures ----------


@pytest.fixture
def fake_user_id() -> int:
    return 10001


@pytest.fixture
def fake_agent_id() -> str:
    return 'agt_demo_1'


@pytest.fixture
def fake_newapi_user_id() -> int:
    return 20001


@pytest.fixture
def fake_newapi_token_id() -> int:
    return 30001


@pytest.fixture
def fake_raw_token_key() -> str:
    """48 字符固定 key（hx + 46）— 与 generate_token_key 输出格式一致"""
    return 'hxAbCdEf' + 'A' * 40


@pytest.fixture
def patched_ensure_newapi_user(fake_user_id, fake_newapi_user_id):
    """patch ensure_newapi_user 返回固定 mapping，避免真连库"""
    fake_mapping = NewApiMappingInfo(
        huanxing_user_id=fake_user_id,
        newapi_user_id=fake_newapi_user_id,
        newapi_token_key='hxParentParentParent',
        app_code='huanxing',
        status='active',
    )
    with patch.object(
        LlmNewapiUserMappingService,
        'ensure_newapi_user',
        new=AsyncMock(return_value=fake_mapping),
    ) as p:
        yield p


def _make_db_returning(scalar_one_or_none_value):
    """构造 mock huanxing db: db.execute(...).scalar_one_or_none() 返回指定值。

    SQLAlchemy 中 Session.add 是 sync，flush/execute 是 async。
    """
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=scalar_one_or_none_value)
    db.execute = AsyncMock(return_value=result)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


def _patch_newapi_direct_dao(generate_key_value: str, create_token_id: int):
    """patch newapi_direct_dao.generate_token_key + create_newapi_token"""
    from backend.app.llm.service import llm_newapi_user_mapping_service as svc_mod

    return patch.multiple(
        svc_mod.newapi_direct_dao,
        generate_token_key=MagicMock(return_value=generate_key_value),
        create_newapi_token=AsyncMock(return_value=create_token_id),
    )


# ---------- ensure_agent_token tests ----------


@pytest.mark.asyncio
async def test_ensure_agent_token_first_time_calls_create_newapi_token_and_writes_lock(
    patched_ensure_newapi_user,
    fake_agent_id,
    fake_user_id,
    fake_newapi_user_id,
    fake_newapi_token_id,
    fake_raw_token_key,
):
    """首次签发：调 create_newapi_token + 写 hermes_agent_llm_token"""
    db = _make_db_returning(None)
    newapi_db = AsyncMock()

    with _patch_newapi_direct_dao(fake_raw_token_key, fake_newapi_token_id):
        result = await LlmNewapiUserMappingService.ensure_agent_token(
            db, newapi_db,
            agent_id=fake_agent_id,
            user_id=fake_user_id,
            model_allowlist=['anthropic/claude-sonnet-4.5'],
            rate_limit_rps=20,
            per_token_quota=100_000,
            name='hermes-agent',
        )

    patched_ensure_newapi_user.assert_awaited_once_with(db, fake_user_id)

    db.add.assert_called_once()
    record = db.add.call_args.args[0]
    assert isinstance(record, HermesAgentLlmToken)
    assert record.agent_id == fake_agent_id
    assert record.user_id == fake_user_id
    assert record.newapi_user_id == fake_newapi_user_id
    assert record.newapi_token_id == fake_newapi_token_id
    assert record.model_allowlist == ['anthropic/claude-sonnet-4.5']
    assert record.rate_limit_rps == 20
    assert record.per_token_quota_remaining == 100_000

    db.flush.assert_awaited_once()

    assert result['agent_id'] == fake_agent_id
    assert result['newapi_user_id'] == fake_newapi_user_id
    assert result['newapi_token_id'] == fake_newapi_token_id
    assert result['token_key_prefix'] == fake_raw_token_key[:8] == 'hxAbCdEf'
    assert result['raw_token_key'] == fake_raw_token_key
    assert result['reused'] is False


@pytest.mark.asyncio
async def test_ensure_agent_token_idempotent_returns_existing_without_recreating(
    patched_ensure_newapi_user,
    fake_agent_id,
    fake_user_id,
    fake_newapi_user_id,
    fake_newapi_token_id,
):
    """同 agent 已有未撤销记录 → 不调 create_newapi_token、不写新行"""
    existing = MagicMock()
    existing.agent_id = fake_agent_id
    existing.newapi_user_id = fake_newapi_user_id
    existing.newapi_token_id = fake_newapi_token_id
    existing.token_key_prefix = 'hxOldOld'
    existing.revoked_at = None

    db = _make_db_returning(existing)
    newapi_db = AsyncMock()

    with _patch_newapi_direct_dao('hxNeverNever', 99999):
        from backend.app.llm.service import llm_newapi_user_mapping_service as svc_mod
        result = await LlmNewapiUserMappingService.ensure_agent_token(
            db, newapi_db,
            agent_id=fake_agent_id,
            user_id=fake_user_id,
        )
        svc_mod.newapi_direct_dao.create_newapi_token.assert_not_awaited()

    db.add.assert_not_called()
    db.flush.assert_not_awaited()

    assert result['raw_token_key'] is None
    assert result['reused'] is True
    assert result['token_key_prefix'] == 'hxOldOld'
    assert result['newapi_token_id'] == fake_newapi_token_id


@pytest.mark.asyncio
async def test_ensure_agent_token_after_revoke_creates_new_token_with_new_token_id(
    patched_ensure_newapi_user,
    fake_agent_id,
    fake_user_id,
    fake_raw_token_key,
):
    """已撤销（revoked_at != NULL）的记录被 WHERE revoked_at IS NULL 过滤掉
    → 重新签发新 token（新 newapi_token_id）"""
    db = _make_db_returning(None)
    newapi_db = AsyncMock()

    new_token_id = 30002
    with _patch_newapi_direct_dao(fake_raw_token_key, new_token_id):
        result = await LlmNewapiUserMappingService.ensure_agent_token(
            db, newapi_db,
            agent_id=fake_agent_id,
            user_id=fake_user_id,
        )

    db.add.assert_called_once()
    record = db.add.call_args.args[0]
    assert record.newapi_token_id == new_token_id
    assert result['newapi_token_id'] == new_token_id
    assert result['raw_token_key'] == fake_raw_token_key


@pytest.mark.asyncio
async def test_token_key_sha256_persisted_not_raw(
    patched_ensure_newapi_user,
    fake_agent_id,
    fake_user_id,
    fake_raw_token_key,
):
    """关键安全断言：DB 里存的是 prefix + sha256(raw)，不能存明文"""
    db = _make_db_returning(None)
    newapi_db = AsyncMock()

    with _patch_newapi_direct_dao(fake_raw_token_key, 30001):
        await LlmNewapiUserMappingService.ensure_agent_token(
            db, newapi_db,
            agent_id=fake_agent_id,
            user_id=fake_user_id,
        )

    db.add.assert_called_once()
    record = db.add.call_args.args[0]

    expected_sha = hashlib.sha256(fake_raw_token_key.encode()).hexdigest()
    assert record.token_key_sha256 == expected_sha
    assert len(record.token_key_sha256) == 64

    # raw key 不能出现在任何持久化字段里
    assert fake_raw_token_key not in (record.token_key_prefix or '')
    assert fake_raw_token_key not in (record.token_key_sha256 or '')

    # prefix 是前 8 字符
    assert record.token_key_prefix == fake_raw_token_key[:8]
    assert len(record.token_key_prefix) == 8


# ---------- revoke_agent_token tests ----------


def _patch_disable_newapi_token(return_value: bool = True):
    from backend.app.llm.service import llm_newapi_user_mapping_service as svc_mod

    return patch.object(
        svc_mod.newapi_direct_dao,
        'disable_newapi_token',
        new=AsyncMock(return_value=return_value),
    )


@pytest.mark.asyncio
async def test_revoke_agent_token_calls_disable_newapi_token_and_marks_revoked_at(
    fake_agent_id, fake_newapi_token_id,
):
    """有未撤销记录 → 调 disable_newapi_token + UPDATE revoked_at = NOW()，返回 True"""
    existing = MagicMock()
    existing.agent_id = fake_agent_id
    existing.newapi_token_id = fake_newapi_token_id
    existing.token_key_prefix = 'hxAbCdEf'
    existing.revoked_at = None

    db = _make_db_returning(existing)
    newapi_db = AsyncMock()

    with _patch_disable_newapi_token(return_value=True):
        from backend.app.llm.service import llm_newapi_user_mapping_service as svc_mod
        ok = await LlmNewapiUserMappingService.revoke_agent_token(db, newapi_db, fake_agent_id)

        # newapi 侧 UPDATE tokens SET status = 2
        svc_mod.newapi_direct_dao.disable_newapi_token.assert_awaited_once_with(
            newapi_db, fake_newapi_token_id,
        )

    assert ok is True

    # huanxing 侧两次 execute：1 次 SELECT（查 existing） + 1 次 UPDATE
    assert db.execute.await_count == 2
    update_clause = db.execute.await_args_list[1].args[0]
    update_sql = str(update_clause)
    assert 'UPDATE' in update_sql.upper()
    assert 'hermes_agent_llm_token' in update_sql

    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_revoke_agent_token_returns_false_when_already_revoked_or_missing(
    fake_agent_id,
):
    """无未撤销记录（已 revoked 或不存在）→ 不调 disable，返回 False，幂等"""
    db = _make_db_returning(None)
    newapi_db = AsyncMock()

    with _patch_disable_newapi_token() as _:
        from backend.app.llm.service import llm_newapi_user_mapping_service as svc_mod
        ok = await LlmNewapiUserMappingService.revoke_agent_token(db, newapi_db, fake_agent_id)
        svc_mod.newapi_direct_dao.disable_newapi_token.assert_not_awaited()

    assert ok is False
    db.flush.assert_not_awaited()


# ---------- rotate_agent_token tests ----------


@pytest.mark.asyncio
async def test_rotate_agent_token_revokes_old_then_creates_new(
    fake_agent_id, fake_user_id, fake_newapi_user_id, fake_raw_token_key,
):
    """rotate = revoke 旧 + ensure 新；必须 disable 旧后才 create 新"""
    call_order: list[str] = []

    fake_revoke = AsyncMock(side_effect=lambda *a, **kw: call_order.append('revoke') or True)
    fake_ensure = AsyncMock(side_effect=lambda *a, **kw: (
        call_order.append('ensure'),
        {
            'agent_id': fake_agent_id,
            'newapi_user_id': fake_newapi_user_id,
            'newapi_token_id': 30002,  # 新 id
            'token_key_prefix': fake_raw_token_key[:8],
            'raw_token_key': fake_raw_token_key,
            'reused': False,
        },
    )[1])

    db = AsyncMock()
    newapi_db = AsyncMock()

    with patch.object(LlmNewapiUserMappingService, 'revoke_agent_token', new=fake_revoke), \
         patch.object(LlmNewapiUserMappingService, 'ensure_agent_token', new=fake_ensure):

        result = await LlmNewapiUserMappingService.rotate_agent_token(
            db, newapi_db, agent_id=fake_agent_id, user_id=fake_user_id,
        )

    # 顺序：revoke 必须在 ensure 之前
    assert call_order == ['revoke', 'ensure']
    fake_revoke.assert_awaited_once_with(db, newapi_db, fake_agent_id)
    fake_ensure.assert_awaited_once()
    # ensure 调用参数：(db, newapi_db, agent_id=..., user_id=...)
    ensure_kwargs = fake_ensure.await_args.kwargs
    assert ensure_kwargs['agent_id'] == fake_agent_id
    assert ensure_kwargs['user_id'] == fake_user_id

    # 返回新 token
    assert result['raw_token_key'] == fake_raw_token_key
    assert result['newapi_token_id'] == 30002
    assert result['reused'] is False


# ---------- get_usage_summary_by_agent tests ----------


@pytest.mark.asyncio
async def test_get_usage_summary_by_agent_resolves_token_id_then_calls_dao(
    fake_agent_id, fake_newapi_token_id,
):
    """先按 agent_id 反查 hermes_agent_llm_token，拿 newapi_token_id 后调 dao"""
    record = MagicMock()
    record.agent_id = fake_agent_id
    record.newapi_token_id = fake_newapi_token_id

    db = _make_db_returning(record)
    newapi_db = AsyncMock()

    fake_rows = [
        {
            'model_name': 'anthropic/claude-sonnet-4.5',
            'prompt_tokens': 1280,
            'completion_tokens': 640,
            'quota': 1920,
            'request_count': 5,
        },
    ]

    from backend.app.llm.service import llm_newapi_user_mapping_service as svc_mod
    with patch.object(
        svc_mod.newapi_direct_dao,
        'get_usage_summary_by_token',
        new=AsyncMock(return_value=fake_rows),
    ) as mocked:
        result = await LlmNewapiUserMappingService.get_usage_summary_by_agent(
            db, newapi_db,
            agent_id=fake_agent_id,
            start_time=1714724000,
            end_time=1714810400,
        )

        mocked.assert_awaited_once_with(
            newapi_db, fake_newapi_token_id, 1714724000, 1714810400,
        )

    assert result == {
        'agent_id': fake_agent_id,
        'period': [1714724000, 1714810400],
        'by_model': fake_rows,
    }


@pytest.mark.asyncio
async def test_get_usage_summary_by_agent_returns_empty_when_no_record(
    fake_agent_id,
):
    """无 hermes_agent_llm_token 记录 → 返回空 by_model，不调 dao"""
    db = _make_db_returning(None)
    newapi_db = AsyncMock()

    from backend.app.llm.service import llm_newapi_user_mapping_service as svc_mod
    with patch.object(
        svc_mod.newapi_direct_dao,
        'get_usage_summary_by_token',
        new=AsyncMock(),
    ) as mocked:
        result = await LlmNewapiUserMappingService.get_usage_summary_by_agent(
            db, newapi_db,
            agent_id=fake_agent_id,
            start_time=0,
            end_time=1,
        )
        mocked.assert_not_awaited()

    assert result == {
        'agent_id': fake_agent_id,
        'period': [0, 1],
        'by_model': [],
    }
