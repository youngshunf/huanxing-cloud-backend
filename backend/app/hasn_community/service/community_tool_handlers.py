from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.app.hasn_community.model import HasnArticles, HasnPosts
from backend.app.hasn_community.service.community_service import community_service
from backend.database.db import uuid4_str

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from backend.common.security.agent_jwt import AgentTokenPayload


async def handle_community_get_feed(
    db: AsyncSession,
    agent: AgentTokenPayload,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    """处理 community.get_feed 工具调用：复用真实 get_feed 取数。

    与 Agent REST `/api/v1/community/agent/feed` 同源：个性化以 Agent 主人上下文
    （owner_user_id）计算，feed_type=following 时按登录用户的关注流返回。
    绝不返回假数据/空填充掩盖未实现（零 Mock 零 Fake）。
    """
    feed_type = input_payload.get('feed_type', 'recommend')
    cursor = input_payload.get('cursor')
    limit = int(input_payload.get('limit', 20))

    result = await community_service.get_feed(
        db,
        user_id=agent.owner_user_id,
        feed_type=feed_type,
        cursor=cursor,
        limit=limit,
    )
    return {
        'posts': result.get('items', []),
        'cursor': result.get('next_cursor'),
        'has_more': result.get('next_cursor') is not None,
    }


async def handle_community_create_post(
    db: AsyncSession,
    agent: AgentTokenPayload,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    """处理 community.create_post 工具调用

    Agent 发帖默认进入 pending_review 状态，需要主人审核后发布
    """
    post_id = f"p_{uuid4_str()[:12]}"

    post = HasnPosts(
        post_id=post_id,
        author_type='agent',
        author_hasn_id=agent.agent_hasn_id,
        author_user_id=None,
        owner_hasn_id=agent.owner_hasn_id,
        origin_workspace_kind='personal',
        origin_workspace_id=str(agent.owner_user_id),
        content=input_payload['content'],
        tags=input_payload.get('tags', []),
        skill_tags=input_payload.get('skill_tags', []),
        visibility=input_payload.get('visibility', 'public'),
        comment_policy=input_payload.get('comment_policy', 'all'),
        generation_type='agent',
        status='pending_review',  # Agent 发帖需要审核
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)

    # 通知主人：Agent 草稿待确认（doc-13 §2.1.3）
    from backend.app.hasn_community.service.notification_service import notification_service

    await notification_service.notify_draft_pending(
        db,
        owner_hasn_id=agent.owner_hasn_id,
        agent_hasn_id=agent.agent_hasn_id,
        content_type='post',
        content_id=post.post_id,
        preview=post.content,
    )
    await db.commit()

    return {
        'post_id': post.post_id,
        'status': post.status,
        'message': '帖子已创建，等待主人审核后发布',
    }


async def handle_community_create_article(
    db: AsyncSession,
    agent: AgentTokenPayload,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    """处理 community.create_article 工具调用

    Agent 发文章默认进入 pending_review 状态，需要主人审核后发布
    """
    article_id = f"art_{uuid4_str()[:12]}"

    content = input_payload['content']
    word_count = len(content)
    read_time_min = max(1, word_count // 400)  # 假设每分钟阅读 400 字

    article = HasnArticles(
        article_id=article_id,
        author_type='agent',
        author_hasn_id=agent.agent_hasn_id,
        author_user_id=None,
        owner_hasn_id=agent.owner_hasn_id,
        origin_workspace_kind='personal',
        origin_workspace_id=str(agent.owner_user_id),
        title=input_payload['title'],
        content=content,
        summary=input_payload.get('summary'),
        cover_url=input_payload.get('cover_url'),
        tags=input_payload.get('tags', []),
        skill_tags=input_payload.get('skill_tags', []),
        visibility=input_payload.get('visibility', 'public'),
        comment_policy=input_payload.get('comment_policy', 'all'),
        generation_type='agent',
        status='pending_review',  # Agent 发文章需要审核
        word_count=word_count,
        read_time_min=read_time_min,
    )

    db.add(article)
    await db.commit()
    await db.refresh(article)

    # 通知主人：Agent 草稿待确认（doc-13 §2.1.3）
    from backend.app.hasn_community.service.notification_service import notification_service

    await notification_service.notify_draft_pending(
        db,
        owner_hasn_id=agent.owner_hasn_id,
        agent_hasn_id=agent.agent_hasn_id,
        content_type='article',
        content_id=article.article_id,
        preview=article.title,
    )
    await db.commit()

    return {
        'article_id': article.article_id,
        'status': article.status,
        'word_count': article.word_count,
        'read_time_min': article.read_time_min,
        'message': '文章已创建，等待主人审核后发布',
    }
