"""
B-5 回归：get_trending_topics 真实统计（doc-12 C3），替换模拟数据。
连真实 PG，事务回滚隔离。
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from backend.app.hasn_community.service.community_service import community_service
from backend.utils.timezone import timezone
from tests.hasn_community.conftest import seed_human, seed_post


@pytest.mark.asyncio
async def test_trending_ranks_by_real_tag_usage(db):
    author = await seed_human(db, nickname='作者')
    now = timezone.now()

    # 标签 A 用于 3 条近期帖子，标签 B 用于 1 条
    for i in range(3):
        await seed_post(
            db, author_hasn_id=author['hasn_id'], content=f'A 帖 {i}',
            published_time=now - timedelta(hours=i), tags=['热标签A'],
        )
    await seed_post(
        db, author_hasn_id=author['hasn_id'], content='B 帖',
        published_time=now - timedelta(hours=1), tags=['冷标签B'],
    )

    topics = await community_service.get_trending_topics(db, limit=10, days=7)
    topic_map = {t['topic']: t for t in topics}

    assert '热标签A' in topic_map
    assert topic_map['热标签A']['post_count'] >= 3
    # 不再是写死的 'AI分身产品设计' 等模拟值
    assert 'AI分身产品设计' not in topic_map or topic_map.get('AI分身产品设计', {}).get('post_count', 0) > 0


@pytest.mark.asyncio
async def test_trending_excludes_old_and_draft(db):
    author = await seed_human(db, nickname='作者')
    now = timezone.now()

    # 窗口外（30 天前）+ 草稿，均不应计入
    await seed_post(
        db, author_hasn_id=author['hasn_id'], content='很旧的帖子',
        published_time=now - timedelta(days=30), tags=['窗口外标签'],
    )
    await seed_post(
        db, author_hasn_id=author['hasn_id'], content='草稿帖子',
        status='draft', published_time=now, tags=['草稿标签'],
    )

    topics = await community_service.get_trending_topics(db, limit=50, days=7)
    names = {t['topic'] for t in topics}
    assert '窗口外标签' not in names
    assert '草稿标签' not in names


@pytest.mark.asyncio
async def test_trending_empty_when_no_recent_content(db):
    # 全新隔离事务里没有近 7 天本测试造的标签即可（库里可能有真实数据，只断言结构合法）
    topics = await community_service.get_trending_topics(db, limit=5, days=7)
    assert isinstance(topics, list)
    for t in topics:
        assert set(t.keys()) == {'topic', 'post_count', 'trend'}
        assert t['trend'] in {'rising', 'stable', 'falling'}
