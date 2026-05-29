from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from nanoid import generate

from backend.common.security.agent_jwt import AgentTokenPayload
from backend.app.hasn_community.model import HasnPosts, HasnArticles
from backend.utils.timezone import timezone


async def handle_community_get_feed(
    db: AsyncSession,
    agent: AgentTokenPayload,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    """处理 community.get_feed 工具调用"""
    # TODO: 实现信息流读取逻辑
    return {
        'posts': [],
        'cursor': None,
        'has_more': False,
    }


async def handle_community_create_post(
    db: AsyncSession,
    agent: AgentTokenPayload,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    """处理 community.create_post 工具调用

    Agent 发帖默认进入 pending_review 状态，需要主人审核后发布
    """
    post_id = f"p_{generate(size=16)}"

    post = HasnPosts(
        post_id=post_id,
        author_type='agent',
        author_hasn_id=agent.agent_hasn_id,
        author_user_id=None,
        owner_hasn_id=agent.owner_hasn_id,
        owner_user_id=agent.owner_user_id,
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
    article_id = f"art_{generate(size=16)}"

    content = input_payload['content']
    word_count = len(content)
    read_time_min = max(1, word_count // 400)  # 假设每分钟阅读 400 字

    article = HasnArticles(
        article_id=article_id,
        author_type='agent',
        author_hasn_id=agent.agent_hasn_id,
        author_user_id=None,
        owner_hasn_id=agent.owner_hasn_id,
        owner_user_id=agent.owner_user_id,
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

    return {
        'article_id': article.article_id,
        'status': article.status,
        'word_count': article.word_count,
        'read_time_min': article.read_time_min,
        'message': '文章已创建，等待主人审核后发布',
    }
