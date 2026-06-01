"""
文章流回归：get_feed(feed_type='articles') 取 hasn_articles + 推荐文章。

根因修复：旧 get_feed 只查 hasn_posts，feed_type='articles' 实际返回帖子，
导致"发布的文章不显示、点击显示帖子"。本测试锁住文章流取数、私密过滤、
content_type 标记、互动态回填、游标分页与推荐文章列表。连真实 PG，事务回滚隔离。
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from backend.app.hasn_community.service.community_service import community_service
from backend.utils.timezone import timezone
from tests.hasn_community.conftest import (
    seed_article,
    seed_collection_item,
    seed_human,
    seed_post,
)


@pytest.mark.asyncio
async def test_articles_feed_returns_articles_not_posts(db):
    """feed_type='articles' 只返回 hasn_articles 的文章，且带 content_type='article'。"""
    author = await seed_human(db, nickname='文章作者')
    aid = await seed_article(db, author_hasn_id=author['hasn_id'], title='我的第一篇文章')
    pid = await seed_post(db, author_hasn_id=author['hasn_id'], content='这是一条帖子')

    result = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='articles', limit=50
    )

    article_ids = [it['article_id'] for it in result['items']]
    assert aid in article_ids
    # 帖子不应出现在文章流里
    assert all(it.get('content_type') == 'article' for it in result['items'])
    assert all('post_id' not in it for it in result['items'])
    assert pid not in article_ids

    target = next(it for it in result['items'] if it['article_id'] == aid)
    assert target['title'] == '我的第一篇文章'
    assert target['author']['hasn_id'] == author['hasn_id']
    assert 'read_time_min' in target


@pytest.mark.asyncio
async def test_articles_feed_excludes_private(db):
    """私密文章不进入公共文章流。"""
    author = await seed_human(db, nickname='私密作者')
    public_id = await seed_article(db, author_hasn_id=author['hasn_id'], title='公开文章', visibility='public')
    private_id = await seed_article(
        db, author_hasn_id=author['hasn_id'], title='私密文章', visibility='private'
    )

    result = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='articles', limit=50
    )
    ids = [it['article_id'] for it in result['items']]
    assert public_id in ids
    assert private_id not in ids


@pytest.mark.asyncio
async def test_articles_feed_cursor_pagination(db):
    """文章流 keyset 游标：分页无重叠、可终止。"""
    author = await seed_human(db, nickname='多产文章作者')
    base = timezone.now()
    created = []
    for i in range(5):
        aid = await seed_article(
            db,
            author_hasn_id=author['hasn_id'],
            title=f'文章 {i}',
            published_time=base - timedelta(minutes=i),
        )
        created.append(aid)

    page1 = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='articles', limit=2
    )
    assert len(page1['items']) == 2
    assert page1['next_cursor'] is not None

    page2 = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='articles', limit=2, cursor=page1['next_cursor']
    )
    ids1 = {it['article_id'] for it in page1['items']}
    ids2 = {it['article_id'] for it in page2['items']}
    assert ids1.isdisjoint(ids2)


@pytest.mark.asyncio
async def test_articles_feed_reflects_like_and_collect(db):
    """文章流回填 viewer 的 is_liked/is_collected（target_type='article'）。"""
    viewer = await seed_human(db, nickname='文章互动者')
    author = await seed_human(db, nickname='被互动文章作者')
    aid = await seed_article(db, author_hasn_id=author['hasn_id'], title='可被互动的文章')

    await community_service.create_like(
        db, user_id=viewer['user_id'], hasn_id=viewer['hasn_id'], target_type='article', target_id=aid
    )
    await seed_collection_item(db, owner_hasn_id=viewer['hasn_id'], target_type='article', target_id=aid)

    result = await community_service.get_feed(
        db, user_id=viewer['user_id'], feed_type='articles', limit=50
    )
    target = next((it for it in result['items'] if it['article_id'] == aid), None)
    assert target is not None
    assert target['is_liked'] is True
    assert target['is_collected'] is True


@pytest.mark.asyncio
async def test_articles_feed_keyword_search(db):
    """文章流关键词：q 命中标题/摘要/正文。"""
    author = await seed_human(db, nickname='文章搜索作者')
    hit = await seed_article(
        db, author_hasn_id=author['hasn_id'], title='向量检索实战', content='正文与向量无关词'
    )
    miss = await seed_article(db, author_hasn_id=author['hasn_id'], title='今天的随笔', content='闲聊')

    result = await community_service.get_feed(
        db, user_id=author['user_id'], feed_type='articles', q='向量检索', limit=50
    )
    ids = [it['article_id'] for it in result['items']]
    assert hit in ids
    assert miss not in ids


@pytest.mark.asyncio
async def test_recommended_articles_returns_recent_published(db):
    """推荐文章：返回近 N 篇已发布、非私密文章，按发布时间倒序的轻量列表。"""
    author = await seed_human(db, nickname='推荐文章作者')
    base = timezone.now()
    newest = await seed_article(
        db, author_hasn_id=author['hasn_id'], title='最新文章', published_time=base
    )
    await seed_article(
        db, author_hasn_id=author['hasn_id'], title='较旧文章', published_time=base - timedelta(hours=1)
    )
    await seed_article(
        db, author_hasn_id=author['hasn_id'], title='私密不推荐', visibility='private'
    )

    items = await community_service.get_recommended_articles(
        db, viewer_user_id=author['user_id'], limit=5
    )
    assert len(items) >= 2
    ids = [it['article_id'] for it in items]
    assert newest in ids
    # 私密文章不进推荐
    titles = [it['title'] for it in items]
    assert '私密不推荐' not in titles
    # 轻量字段齐全
    first = items[0]
    assert 'title' in first and 'author' in first and 'read_time_min' in first
