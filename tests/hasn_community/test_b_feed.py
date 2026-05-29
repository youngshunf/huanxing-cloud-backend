"""
B-1/2/3 回归：get_feed 关注流 + 游标分页 + is_liked/is_collected。

对应 docs/.../12 C1、docs/.../13 §2.4。连真实 PG，事务回滚隔离。
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from backend.app.hasn_community.service.community_service import community_service
from backend.utils.timezone import timezone
from tests.hasn_community.conftest import (
    seed_collection_item,
    seed_human,
    seed_post,
)


@pytest.mark.asyncio
async def test_following_feed_returns_only_followed_authors(db):
    viewer = await seed_human(db, nickname='观察者')
    followed = await seed_human(db, nickname='被关注者')
    other = await seed_human(db, nickname='陌生人')

    p_followed = await seed_post(db, author_hasn_id=followed['hasn_id'], content='关注对象的帖子')
    await seed_post(db, author_hasn_id=other['hasn_id'], content='陌生人的帖子')

    # viewer 关注 followed
    await community_service.create_follow(
        db,
        user_id=viewer['user_id'],
        hasn_id=viewer['hasn_id'],
        target_type='human',
        target_hasn_id=followed['hasn_id'],
    )

    result = await community_service.get_feed(
        db, user_id=viewer['user_id'], feed_type='following', limit=20
    )
    post_ids = [it['post_id'] for it in result['items']]
    assert p_followed in post_ids
    assert all(it['author']['hasn_id'] == followed['hasn_id'] for it in result['items'])


@pytest.mark.asyncio
async def test_following_feed_empty_without_identity(db):
    result = await community_service.get_feed(
        db, user_id=None, feed_type='following', limit=20
    )
    assert result['items'] == []
    assert result['next_cursor'] is None


@pytest.mark.asyncio
async def test_cursor_pagination_no_overlap_and_terminates(db):
    author = await seed_human(db, nickname='多产作者')
    base = timezone.now()
    # 5 条帖子，递减发布时间，保证 keyset 顺序确定
    created = []
    for i in range(5):
        pid = await seed_post(
            db,
            author_hasn_id=author['hasn_id'],
            content=f'帖子 {i}',
            published_time=base - timedelta(minutes=i),
        )
        created.append(pid)

    page1 = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='recommend', limit=2
    )
    assert len(page1['items']) == 2
    assert page1['next_cursor'] is not None

    page2 = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='recommend', limit=2, cursor=page1['next_cursor']
    )
    assert len(page2['items']) == 2

    ids1 = {it['post_id'] for it in page1['items']}
    ids2 = {it['post_id'] for it in page2['items']}
    assert ids1.isdisjoint(ids2)  # 无重叠

    page3 = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='recommend', limit=2, cursor=page2['next_cursor']
    )
    # 仅剩这位作者的 5 条里第 5 条（库里可能有其它已发布帖子，故只断言包含关系与翻页推进）
    seen = ids1 | ids2 | {it['post_id'] for it in page3['items']}
    for pid in created:
        assert pid in seen


@pytest.mark.asyncio
async def test_is_liked_and_is_collected_reflect_real_state(db):
    viewer = await seed_human(db, nickname='互动者')
    author = await seed_human(db, nickname='作者')
    pid = await seed_post(db, author_hasn_id=author['hasn_id'], content='可被互动的帖子')

    # 初始：都为 False
    detail0 = await community_service.get_post(db, post_id=pid, user_id=viewer['user_id'])
    assert detail0['is_liked'] is False
    assert detail0['is_collected'] is False

    # 点赞 + 收藏
    await community_service.create_like(
        db, user_id=viewer['user_id'], hasn_id=viewer['hasn_id'], target_type='post', target_id=pid
    )
    await seed_collection_item(db, owner_hasn_id=viewer['hasn_id'], target_type='post', target_id=pid)

    detail1 = await community_service.get_post(db, post_id=pid, user_id=viewer['user_id'])
    assert detail1['is_liked'] is True
    assert detail1['is_collected'] is True

    # feed 中同样回显
    feed = await community_service.get_feed(
        db, user_id=viewer['user_id'], feed_type='recommend', limit=50
    )
    target = next((it for it in feed['items'] if it['post_id'] == pid), None)
    assert target is not None
    assert target['is_liked'] is True
    assert target['is_collected'] is True

    # 其它用户视角：未点赞未收藏
    other = await seed_human(db, nickname='路人')
    detail_other = await community_service.get_post(db, post_id=pid, user_id=other['user_id'])
    assert detail_other['is_liked'] is False
    assert detail_other['is_collected'] is False
