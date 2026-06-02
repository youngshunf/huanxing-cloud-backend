"""投递策略解析单元测试（§4.3 / §4.4）——纯函数，不依赖 DB。"""
from __future__ import annotations

from datetime import datetime

from backend.app.notification.service.delivery_policy import default_priority, resolve_policy


class _Pref:
    """模拟 HasnNotificationPreferences 行。"""

    def __init__(self, channels=None, dnd=None) -> None:
        self.channels = channels or {}
        self.dnd = dnd or {}


def test_category_default_channels_and_priority() -> None:
    p = resolve_policy(category='contact', priority=default_priority('contact'))
    assert p['priority'] == 'high'
    assert p['channels']['center'] is True
    assert p['channels']['card_message'] is True
    assert p['channels']['toast'] is True
    assert p['channels']['push'] is False


def test_social_default_is_quiet() -> None:
    p = resolve_policy(category='social', priority=default_priority('social'))
    assert p['channels']['toast'] is False
    assert p['channels']['push'] is False
    assert p['channels']['center'] is True


def test_owner_pref_overrides_channel() -> None:
    pref = _Pref(channels={'card_message': False})
    p = resolve_policy(category='contact', priority='high', owner_pref=pref)
    assert p['channels']['card_message'] is False  # 主人关掉卡片承载
    assert p['channels']['center'] is True          # center 不可关


def test_center_cannot_be_disabled_by_pref() -> None:
    pref = _Pref(channels={'center': False})
    p = resolve_policy(category='system', priority='high', owner_pref=pref)
    assert p['channels']['center'] is True


def test_dnd_suppresses_noisy_channels_in_window() -> None:
    pref = _Pref(dnd={'enabled': True, 'start': '22:00', 'end': '08:00', 'allow_critical': True})
    night = datetime(2026, 6, 2, 23, 30)  # 落在 22:00-08:00
    p = resolve_policy(category='system', priority='high', owner_pref=pref, now=night)
    assert p['dnd_suppressed'] is True
    assert p['channels']['toast'] is False
    assert p['channels']['push'] is False
    assert p['channels']['center'] is True  # center 永远留底


def test_dnd_not_triggered_outside_window() -> None:
    pref = _Pref(dnd={'enabled': True, 'start': '22:00', 'end': '08:00'})
    day = datetime(2026, 6, 2, 12, 0)
    p = resolve_policy(category='reminder', priority='high', owner_pref=pref, now=day)
    assert p['dnd_suppressed'] is False
    assert p['channels']['toast'] is True  # reminder 默认开 toast


def test_dnd_critical_bypass() -> None:
    pref = _Pref(dnd={'enabled': True, 'start': '22:00', 'end': '08:00', 'allow_critical': True})
    night = datetime(2026, 6, 2, 23, 30)
    p = resolve_policy(category='system', priority='critical', owner_pref=pref, now=night)
    assert p['dnd_suppressed'] is False  # critical 不被免打扰压
    assert p['channels']['toast'] is True


def test_dnd_midnight_wrap_morning() -> None:
    pref = _Pref(dnd={'enabled': True, 'start': '22:00', 'end': '08:00'})
    early = datetime(2026, 6, 2, 7, 0)  # 07:00 仍在窗口内（跨午夜）
    p = resolve_policy(category='message', priority='normal', owner_pref=pref, now=early)
    assert p['dnd_suppressed'] is True
    assert p['channels']['push'] is False
