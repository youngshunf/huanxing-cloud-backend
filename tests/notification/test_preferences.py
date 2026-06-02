"""主人通知偏好 CRUD + 生效解析（§4.4）——连真库，事务回滚隔离。"""
from __future__ import annotations

import pytest

from backend.app.notification.service.notification_service import notification_service
from tests.notification.conftest import seed_human


@pytest.mark.asyncio
async def test_upsert_creates_then_updates(db) -> None:
    owner = await seed_human(db, nickname='主人')
    r1 = await notification_service.upsert_preference(
        db, owner_id=owner['hasn_id'], category='*', channels={'toast': False}
    )
    assert r1['channels'] == {'toast': False}

    r2 = await notification_service.upsert_preference(
        db, owner_id=owner['hasn_id'], category='*', channels={'toast': True, 'push': False}
    )
    assert r2['channels'] == {'toast': True, 'push': False}

    items = await notification_service.list_preferences(db, owner_id=owner['hasn_id'])
    assert len(items) == 1  # 同 owner+category 唯一


@pytest.mark.asyncio
async def test_specific_category_beats_global_default(db) -> None:
    owner = await seed_human(db, nickname='主人')
    # 全局默认关 toast；contact 专属偏好开 toast
    await notification_service.upsert_preference(
        db, owner_id=owner['hasn_id'], category='*', channels={'toast': False}
    )
    await notification_service.upsert_preference(
        db, owner_id=owner['hasn_id'], category='contact', channels={'toast': True}
    )
    pref = await notification_service._get_effective_preference(
        db, owner_id=owner['hasn_id'], category='contact'
    )
    assert pref is not None
    assert pref.category == 'contact'
    assert pref.channels == {'toast': True}


@pytest.mark.asyncio
async def test_global_default_used_when_no_specific(db) -> None:
    owner = await seed_human(db, nickname='主人')
    await notification_service.upsert_preference(
        db, owner_id=owner['hasn_id'], category='*', channels={'push': False}
    )
    pref = await notification_service._get_effective_preference(
        db, owner_id=owner['hasn_id'], category='social'
    )
    assert pref is not None
    assert pref.category == '*'


@pytest.mark.asyncio
async def test_dnd_preference_suppresses_toast_via_emit(db) -> None:
    owner = await seed_human(db, nickname='主人')
    # 全局免打扰 00:00-23:59（确保命中），allow_critical 默认 True
    await notification_service.upsert_preference(
        db,
        owner_id=owner['hasn_id'],
        category='*',
        dnd={'enabled': True, 'start': '00:00', 'end': '23:59', 'allow_critical': True},
    )
    nid = await notification_service.emit(
        db,
        recipient_id=owner['hasn_id'],
        source={'kind': 'system'},
        category='reminder',
        type='event_reminder',
        title='日程提醒',
        priority='high',
        payload={'target': {'type': 'event', 'id': 'e1'}},
    )
    from sqlalchemy import select

    from backend.app.hasn.model.hasn_notifications import HasnNotifications

    row = (await db.execute(select(HasnNotifications).where(HasnNotifications.id == nid))).scalar_one()
    assert row.delivery['dnd_suppressed'] is True
    assert row.delivery['channels']['toast'] is False
    assert row.delivery['channels']['center'] is True
