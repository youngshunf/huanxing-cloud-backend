"""投递策略解析（§4.3 / §4.4）。

最终投递策略 = category 默认 ⊕ 主人偏好覆盖 ⊕ 来源 delivery_hint。
center 不可关（通知中心是权威记录，D1）；DND 只压"吵"的承载（toast/push）。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime

# category → (默认渠道集合, 默认优先级)。center 永远 True。
# 渠道键：center / card_message / toast / push / badge
CATEGORY_DEFAULTS: dict[str, dict[str, Any]] = {
    'social': {'channels': {'center': True, 'badge': True}, 'priority': 'normal'},
    'contact': {'channels': {'center': True, 'card_message': True, 'toast': True}, 'priority': 'high'},
    'message': {'channels': {'center': True, 'badge': True, 'push': True}, 'priority': 'normal'},
    'agent': {'channels': {'center': True, 'card_message': True}, 'priority': 'normal'},
    'app': {'channels': {'center': True}, 'priority': 'normal'},
    'commerce': {'channels': {'center': True, 'card_message': True}, 'priority': 'high'},
    'system': {'channels': {'center': True, 'card_message': True, 'toast': True, 'push': True}, 'priority': 'high'},
    'reminder': {'channels': {'center': True, 'toast': True, 'push': True}, 'priority': 'high'},
}

ALL_CHANNELS = ('center', 'card_message', 'toast', 'push', 'badge')
# 免打扰命中时被抑制的"吵"渠道
NOISY_CHANNELS = ('toast', 'push')

_DEFAULT_CATEGORY = {'channels': {'center': True}, 'priority': 'normal'}


def default_priority(category: str) -> str:
    return CATEGORY_DEFAULTS.get(category, _DEFAULT_CATEGORY)['priority']


def _base_channels(category: str) -> dict[str, bool]:
    spec = CATEGORY_DEFAULTS.get(category, _DEFAULT_CATEGORY)['channels']
    return {ch: bool(spec.get(ch, False)) for ch in ALL_CHANNELS}


def _in_dnd_window(now: datetime, start: str, end: str) -> bool:
    """now 的本地 HH:MM 是否落在 [start,end] 窗口（支持跨午夜）。"""
    try:
        t = now.strftime('%H:%M')
    except (ValueError, AttributeError):
        return False
    if start == end:
        return False
    if start < end:
        return start <= t < end
    # 跨午夜：22:00–08:00
    return t >= start or t < end


def resolve_policy(
    *,
    category: str,
    priority: str,
    owner_pref: Any | None = None,
    delivery_hint: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """解析有效投递策略。

    owner_pref: HasnNotificationPreferences 行（或 None）。其 channels 覆盖各承载开关，
                dnd 决定免打扰抑制。
    delivery_hint: 来源建议（仅能在"已开"基础上进一步收敛/打开 app 自有承载，受最终偏好约束）。
    返回 {channels: {...}, dnd_suppressed: bool, priority: str}。
    """
    channels = _base_channels(category)

    # 1) 主人偏好覆盖渠道开关
    pref_channels: dict[str, Any] = {}
    pref_dnd: dict[str, Any] = {}
    if owner_pref is not None:
        pref_channels = getattr(owner_pref, 'channels', None) or {}
        pref_dnd = getattr(owner_pref, 'dnd', None) or {}
    for ch, val in pref_channels.items():
        if ch in channels and isinstance(val, bool):
            channels[ch] = val

    # 2) 来源 delivery_hint：只能在偏好允许范围内表达（不能强开主人关掉的渠道）
    if delivery_hint:
        hint_channels = delivery_hint.get('channels', {}) if isinstance(delivery_hint, dict) else {}
        for ch, val in hint_channels.items():
            if ch in channels and isinstance(val, bool):
                # hint 只能在主人未显式关闭时收敛为 False，或开启 app/card 自有承载
                if val is False:
                    channels[ch] = False
                elif ch not in pref_channels:
                    channels[ch] = True

    # 3) center 永远不可关（D1）
    channels['center'] = True

    # 4) 免打扰：命中窗口抑制 toast/push（critical 且 allow_critical 不抑制）
    dnd_suppressed = False
    if pref_dnd.get('enabled') and now is not None:
        allow_critical = pref_dnd.get('allow_critical', True)
        if not (priority == 'critical' and allow_critical):
            if _in_dnd_window(now, pref_dnd.get('start', '22:00'), pref_dnd.get('end', '08:00')):
                dnd_suppressed = True
                for ch in NOISY_CHANNELS:
                    channels[ch] = False

    return {'channels': channels, 'dnd_suppressed': dnd_suppressed, 'priority': priority}
