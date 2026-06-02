"""统一通知 emit() 集成测试（§5）——连真库，事务回滚隔离。"""
from __future__ import annotations

import pytest

from backend.app.notification.service.notification_service import notification_service
from tests.notification.conftest import seed_human, seed_preference


@pytest.mark.asyncio
async def test_emit_lands_authoritative_row(db) -> None:
    owner = await seed_human(db, nickname='主人')
    nid = await notification_service.emit(
        db,
        recipient_id=owner['hasn_id'],
        source={'kind': 'system', 'id': 'announcement', 'display_name': '唤星官方'},
        category='system',
        type='announcement',
        title='系统公告',
        body='正文',
        payload={'target': {'type': 'sys', 'id': 'x1'}, 'link': '/x'},
    )
    assert isinstance(nid, int)

    notes = await notification_service.list_notifications(db, recipient_hasn_id=owner['hasn_id'])
    assert len(notes['items']) == 1
    item = notes['items'][0]
    assert item['id'] == nid
    assert item['category'] == 'system'
    assert item['priority'] == 'high'          # system 默认 high
    assert item['source']['kind'] == 'system'
    assert item['state'] == 'unread'
    assert item['read'] is False


@pytest.mark.asyncio
async def test_emit_default_group_key_aggregates(db) -> None:
    owner = await seed_human(db, nickname='主人')
    # 同 type + 同 target → 同 group_key → 读时折叠为一条，aggregated_count 累加
    for _ in range(3):
        await notification_service.emit(
            db,
            recipient_id=owner['hasn_id'],
            source={'kind': 'user', 'id': 'u1', 'display_name': '甲'},
            category='social',
            type='community_like',
            title='甲赞了你的帖子',
            payload={'target': {'type': 'post', 'id': 'p_same'}},
        )
    notes = await notification_service.list_notifications(db, recipient_hasn_id=owner['hasn_id'])
    assert len(notes['items']) == 1
    assert notes['items'][0]['aggregated_count'] == 3


@pytest.mark.asyncio
async def test_emit_dedupe_key_collapses_into_single_row(db) -> None:
    owner = await seed_human(db, nickname='主人')
    nid1 = await notification_service.emit(
        db,
        recipient_id=owner['hasn_id'],
        source={'kind': 'system', 'id': 'sec'},
        category='system',
        type='security',
        title='登录提醒',
        dedupe_key='login:dev1',
        payload={'target': {'type': 'sec', 'id': 'dev1'}},
    )
    nid2 = await notification_service.emit(
        db,
        recipient_id=owner['hasn_id'],
        source={'kind': 'system', 'id': 'sec'},
        category='system',
        type='security',
        title='登录提醒(2)',
        dedupe_key='login:dev1',
        payload={'target': {'type': 'sec', 'id': 'dev1'}},
    )
    assert nid1 == nid2  # 命中 dedupe → 同一行
    uc = await notification_service.unread_count(db, recipient_hasn_id=owner['hasn_id'])
    assert uc['total'] == 1


@pytest.mark.asyncio
async def test_emit_records_delivery_policy(db) -> None:
    owner = await seed_human(db, nickname='主人')
    # 主人关掉 contact 的卡片承载
    await seed_preference(db, owner_id=owner['hasn_id'], category='contact',
                          channels={'card_message': False})
    nid = await notification_service.emit(
        db,
        recipient_id=owner['hasn_id'],
        source={'kind': 'user', 'id': 'u2', 'display_name': '乙'},
        category='contact',
        type='contact_request',
        title='乙 请求加你好友',
        payload={'target': {'type': 'human', 'id': 'u2'}},
    )
    from sqlalchemy import select

    from backend.app.hasn.model.hasn_notifications import HasnNotifications

    row = (await db.execute(select(HasnNotifications).where(HasnNotifications.id == nid))).scalar_one()
    assert row.delivery['channels']['card_message'] is False  # 偏好生效
    assert row.delivery['channels']['center'] is True


@pytest.mark.asyncio
async def test_unread_count_by_category(db) -> None:
    owner = await seed_human(db, nickname='主人')
    await notification_service.emit(
        db, recipient_id=owner['hasn_id'], source={'kind': 'system'},
        category='system', type='announcement', title='公告',
        payload={'target': {'type': 's', 'id': 'a'}},
    )
    await notification_service.emit(
        db, recipient_id=owner['hasn_id'], source={'kind': 'user'},
        category='social', type='community_like', title='点赞',
        payload={'target': {'type': 'post', 'id': 'p1'}},
    )
    uc = await notification_service.unread_count(db, recipient_hasn_id=owner['hasn_id'])
    assert uc['total'] == 2
    assert uc['by_category'].get('system') == 1
    assert uc['by_category'].get('social') == 1


@pytest.mark.asyncio
async def test_category_filter_in_list(db) -> None:
    owner = await seed_human(db, nickname='主人')
    await notification_service.emit(
        db, recipient_id=owner['hasn_id'], source={'kind': 'system'},
        category='system', type='announcement', title='公告',
        payload={'target': {'type': 's', 'id': 'a'}},
    )
    await notification_service.emit(
        db, recipient_id=owner['hasn_id'], source={'kind': 'agent'},
        category='agent', type='task_result', title='任务完成',
        payload={'target': {'type': 'task', 'id': 't1'}},
    )
    only_agent = await notification_service.list_notifications(
        db, recipient_hasn_id=owner['hasn_id'], categories=['agent']
    )
    assert len(only_agent['items']) == 1
    assert only_agent['items'][0]['category'] == 'agent'


@pytest.mark.asyncio
async def test_mark_read_writes_state_and_read(db) -> None:
    owner = await seed_human(db, nickname='主人')
    nid = await notification_service.emit(
        db, recipient_id=owner['hasn_id'], source={'kind': 'system'},
        category='system', type='announcement', title='公告',
        payload={'target': {'type': 's', 'id': 'a'}},
    )
    await notification_service.mark_read(db, recipient_hasn_id=owner['hasn_id'], notification_id=nid)
    from sqlalchemy import select

    from backend.app.hasn.model.hasn_notifications import HasnNotifications

    row = (await db.execute(select(HasnNotifications).where(HasnNotifications.id == nid))).scalar_one()
    assert row.read is True
    assert row.state == 'read'


@pytest.mark.asyncio
async def test_mark_read_others_forbidden(db) -> None:
    owner = await seed_human(db, nickname='主人')
    other = await seed_human(db, nickname='他人')
    nid = await notification_service.emit(
        db, recipient_id=owner['hasn_id'], source={'kind': 'system'},
        category='system', type='announcement', title='公告',
        payload={'target': {'type': 's', 'id': 'a'}},
    )
    from backend.common.exception import errors

    with pytest.raises(errors.NotFoundError):
        await notification_service.mark_read(
            db, recipient_hasn_id=other['hasn_id'], notification_id=nid
        )


@pytest.mark.asyncio
async def test_emit_rejects_empty_recipient(db) -> None:
    from backend.common.exception import errors

    with pytest.raises(errors.RequestError):
        await notification_service.emit(
            db, recipient_id='', source={'kind': 'system'},
            category='system', type='x', title='t', payload={},
        )
