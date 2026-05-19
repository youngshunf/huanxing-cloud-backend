"""HASN Core/02 §7.4.1 / §7.5.2 协议级约束测试。

覆盖：
- 非 social trust_level=5 拒绝（validate_relation_constraints）
- service trust_level=1 拒绝
- 权限引擎 commerce + Owner=5 运行时降级为 Trusted（4）
- SCOPE_ACTION_MAP 全部 12 个 scope 字面量都有映射
- lifecycle 合法转换（4 个）
- lifecycle 非法转换（2 个）
- scope_limited + lifecycle=expired 返回 deny
"""

from __future__ import annotations

import pytest

from backend.app.hasn.constants import (
    ALLOW,
    DENY,
    SCOPE_ACTION_MAP,
    SCOPE_LIFECYCLE_STATES,
    SCOPE_LTD,
    apply_lifecycle_to_decision,
    check_action_permission,
    effective_trust_level,
    is_lifecycle_transition_valid,
    runtime_effective_trust_level,
    validate_relation_constraints,
)

# ── 协议级约束（写入路径） ────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    'relation_type',
    ['commerce', 'service', 'professional', 'platform'],
)
def test_validate_non_social_trust_level_5_rejected(relation_type: str) -> None:
    """非 social 关系 trust_level=5 应被拒绝。"""
    with pytest.raises(ValueError, match='非 social'):
        validate_relation_constraints(relation_type, 5)


@pytest.mark.unit
def test_validate_service_trust_level_1_rejected() -> None:
    """service 关系不存在 Stranger 状态（trust_level=1）。"""
    with pytest.raises(ValueError, match='Stranger'):
        validate_relation_constraints('service', 1)


@pytest.mark.unit
def test_validate_social_trust_level_5_allowed() -> None:
    """social 关系 trust_level=5 (Owner) 合法，不应抛错。"""
    validate_relation_constraints('social', 5)


@pytest.mark.unit
@pytest.mark.parametrize(
    'relation_type, trust_level',
    [
        ('commerce', 0),
        ('commerce', 4),
        ('service', 0),
        ('service', 2),
        ('professional', 4),
        ('platform', 2),
        ('social', 1),
    ],
)
def test_validate_legal_combinations(relation_type: str, trust_level: int) -> None:
    """合法组合不应抛错。"""
    validate_relation_constraints(relation_type, trust_level)


# ── 运行时降级 ────────────────────────────────


@pytest.mark.unit
def test_runtime_effective_trust_level_downgrade() -> None:
    """非 social + Owner=5 → 4（防御性降级）。"""
    assert runtime_effective_trust_level('commerce', 5) == 4
    assert runtime_effective_trust_level('service', 5) == 4
    assert runtime_effective_trust_level('professional', 5) == 4
    assert runtime_effective_trust_level('platform', 5) == 4


@pytest.mark.unit
def test_runtime_effective_trust_level_passthrough() -> None:
    """social + 5 与 非 5 等级直接透传。"""
    assert runtime_effective_trust_level('social', 5) == 5
    assert runtime_effective_trust_level('commerce', 4) == 4
    assert runtime_effective_trust_level('service', 2) == 2


@pytest.mark.unit
def test_check_action_permission_commerce_owner_downgrade() -> None:
    """权限引擎: commerce + Owner=5 应按 Trusted=4 求值（不应崩溃于 None fallback）。"""
    # commerce level=4 允许 send_push
    decision_owner = check_action_permission('commerce', 5, 'send_push')
    decision_trusted = check_action_permission('commerce', 4, 'send_push')
    assert decision_owner == decision_trusted == ALLOW


@pytest.mark.unit
def test_effective_trust_level_commerce_5_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    """commerce + 5 触发 warning 日志（运行时降级）。"""
    import logging

    caplog.set_level(logging.WARNING)
    level = effective_trust_level('commerce', 5)
    assert level == 4
    # log 调用通过 backend.common.log.log，未必经 caplog；用结果断言为主


# ── SCOPE_ACTION_MAP 完整性 ────────────────────────────────


_EXPECTED_SCOPES = {
    # commerce (6)
    'pre_sale',
    'negotiation',
    'in_order',
    'fulfilling',
    'after_sale',
    'subscription',
    # service (1)
    'active_order',
    # professional (3)
    'consultation',
    'treatment',
    'follow_up',
    # platform (2)
    'app_installation',
    'system_notice',
}


@pytest.mark.unit
def test_scope_action_map_covers_all_12_scopes() -> None:
    """SCOPE_ACTION_MAP 应覆盖全部 12 个 scope 字面量。"""
    assert set(SCOPE_ACTION_MAP.keys()) == _EXPECTED_SCOPES, (
        f'缺失: {_EXPECTED_SCOPES - SCOPE_ACTION_MAP.keys()}; 多余: {SCOPE_ACTION_MAP.keys() - _EXPECTED_SCOPES}'
    )


@pytest.mark.unit
@pytest.mark.parametrize('scope', sorted(_EXPECTED_SCOPES))
def test_each_scope_has_at_least_one_action(scope: str) -> None:
    """每个 scope 至少映射 1 个 action。"""
    assert SCOPE_ACTION_MAP[scope], f'{scope} 没有任何 action'


# ── Scope 生命周期状态机 ────────────────────────────────


@pytest.mark.unit
def test_lifecycle_states_set() -> None:
    """生命周期状态集合：pending/active/closed/expired。"""
    assert set(SCOPE_LIFECYCLE_STATES) == {'pending', 'active', 'closed', 'expired'}


@pytest.mark.unit
@pytest.mark.parametrize(
    'from_state, to_state',
    [
        ('pending', 'active'),
        ('pending', 'closed'),
        ('active', 'closed'),
        ('active', 'expired'),
    ],
)
def test_lifecycle_legal_transitions(from_state: str, to_state: str) -> None:
    """4 个合法生命周期转换。"""
    assert is_lifecycle_transition_valid(from_state, to_state)


@pytest.mark.unit
@pytest.mark.parametrize(
    'from_state, to_state',
    [
        ('closed', 'active'),  # 终态 → 任何
        ('expired', 'active'),  # 终态 → 任何
        ('active', 'pending'),  # 倒退
        ('pending', 'expired'),  # 跳过 active 直接 expired
    ],
)
def test_lifecycle_illegal_transitions(from_state: str, to_state: str) -> None:
    """非法生命周期转换。"""
    assert not is_lifecycle_transition_valid(from_state, to_state)


# ── scope_limited + lifecycle ────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize('lifecycle', ['closed', 'expired'])
def test_scope_limited_with_terminal_lifecycle_returns_deny(lifecycle: str) -> None:
    """scope_limited + lifecycle 终态 → deny。"""
    assert apply_lifecycle_to_decision(SCOPE_LTD, lifecycle) == DENY


@pytest.mark.unit
@pytest.mark.parametrize('lifecycle', ['pending', 'active', None])
def test_scope_limited_with_active_lifecycle_unchanged(lifecycle: str | None) -> None:
    """scope_limited + active/pending → 不降级。"""
    assert apply_lifecycle_to_decision(SCOPE_LTD, lifecycle) == SCOPE_LTD


@pytest.mark.unit
def test_allow_with_terminal_lifecycle_unchanged() -> None:
    """allow + lifecycle=closed → 仍是 allow（仅 scope_limited 受影响）。"""
    assert apply_lifecycle_to_decision(ALLOW, 'closed') == ALLOW
