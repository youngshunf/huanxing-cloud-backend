"""P2 — 三态能力授权判定（resolve_capability_mode / resolve_tool_mode）单测。

维度① 能力授权：默认全 allow；override 优先；多 scope 取最严；非法值落 allow。
"""

from __future__ import annotations

from backend.common.security.scope_policy import (
    MODE_ALLOW,
    MODE_ASK,
    MODE_DENY,
    resolve_capability_mode,
    resolve_tool_mode,
)


def test_default_mode_when_no_override() -> None:
    assert resolve_capability_mode('allow', {}, 'message:send') == MODE_ALLOW
    assert resolve_capability_mode('ask', {}, 'message:send') == MODE_ASK
    assert resolve_capability_mode('deny', None, 'message:send') == MODE_DENY


def test_override_takes_precedence() -> None:
    caps = {'message:send': 'ask', 'task:create': 'deny'}
    assert resolve_capability_mode('allow', caps, 'message:send') == MODE_ASK
    assert resolve_capability_mode('allow', caps, 'task:create') == MODE_DENY
    # 未 override 的能力落 default
    assert resolve_capability_mode('allow', caps, 'contact:read') == MODE_ALLOW


def test_invalid_values_fall_back_to_allow() -> None:
    assert resolve_capability_mode('garbage', {}, 'x') == MODE_ALLOW
    assert resolve_capability_mode('allow', {'x': 'maybe'}, 'x') == MODE_ALLOW
    assert resolve_capability_mode(None, {}, 'x') == MODE_ALLOW  # type: ignore[arg-type]


def test_resolve_tool_mode_takes_most_restrictive() -> None:
    # 工具需要两个 scope，其中一个被设 deny → 工具整体 deny
    caps = {'message:read': 'deny'}
    assert (
        resolve_tool_mode('allow', caps, tool_name='hasn.message.history', required_scopes=['message:read'])
        == MODE_DENY
    )
    # ask < deny：一个 ask 一个 allow → ask
    caps2 = {'message:send': 'ask'}
    assert (
        resolve_tool_mode('allow', caps2, tool_name='hasn.message.send', required_scopes=['message:send']) == MODE_ASK
    )


def test_resolve_tool_mode_by_tool_name_override() -> None:
    # 按工具 canonical 名 override（13-doc §5.2 ext 工具示例）
    caps = {'hasn.ext.foo.delete': 'deny'}
    assert resolve_tool_mode('allow', caps, tool_name='hasn.ext.foo.delete', required_scopes=['ext:write']) == MODE_DENY


def test_resolve_tool_mode_no_scopes_uses_default() -> None:
    assert resolve_tool_mode('allow', {}, tool_name='hasn.tool.search', required_scopes=[]) == MODE_ALLOW
