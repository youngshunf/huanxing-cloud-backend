"""
B-3 回归（文章侧）：get_article 真实回填 viewer 的 is_liked/is_collected。

此前 get_article 把 is_liked/is_collected 写死 False（TODO 占位），与 get_post
不一致。本用例锁定其与 get_post 同源的真实回填行为。连真实 PG，事务回滚隔离。
"""
from __future__ import annotations

import pytest

from backend.app.hasn_community.service.community_service import community_service
from tests.hasn_community.conftest import seed_collection_item, seed_human


@pytest.mark.asyncio
async def test_get_article_reflects_viewer_like_and_collect(db):
    author = await seed_human(db, nickname='文章作者')
    viewer = await seed_human(db, nickname='文章互动者')

    created = await community_service.create_article(
        db,
        user_id=author['user_id'],
        hasn_id=author['hasn_id'],
        title='可被互动的文章',
        content='正文内容',
    )
    article_id = created['article_id']

    # 初始：viewer 未点赞未收藏 → 均为 False
    detail0 = await community_service.get_article(
        db, user_id=viewer['user_id'], hasn_id=viewer['hasn_id'], article_id=article_id
    )
    assert detail0['is_liked'] is False
    assert detail0['is_collected'] is False

    # 点赞 + 收藏（target_type='article'）
    await community_service.create_like(
        db,
        user_id=viewer['user_id'],
        hasn_id=viewer['hasn_id'],
        target_type='article',
        target_id=article_id,
    )
    await seed_collection_item(
        db, owner_hasn_id=viewer['hasn_id'], target_type='article', target_id=article_id
    )

    detail1 = await community_service.get_article(
        db, user_id=viewer['user_id'], hasn_id=viewer['hasn_id'], article_id=article_id
    )
    assert detail1['is_liked'] is True
    assert detail1['is_collected'] is True


@pytest.mark.asyncio
async def test_get_article_reactions_are_viewer_scoped(db):
    author = await seed_human(db, nickname='作者B')
    viewer = await seed_human(db, nickname='点赞者B')
    other = await seed_human(db, nickname='路人B')

    created = await community_service.create_article(
        db,
        user_id=author['user_id'],
        hasn_id=author['hasn_id'],
        title='隔离校验文章',
        content='正文',
    )
    article_id = created['article_id']

    await community_service.create_like(
        db,
        user_id=viewer['user_id'],
        hasn_id=viewer['hasn_id'],
        target_type='article',
        target_id=article_id,
    )

    # 其它用户视角：不应看到他人的点赞态
    detail_other = await community_service.get_article(
        db, user_id=other['user_id'], hasn_id=other['hasn_id'], article_id=article_id
    )
    assert detail_other['is_liked'] is False
    assert detail_other['is_collected'] is False
