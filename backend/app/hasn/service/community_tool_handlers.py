"""
社区 Tool Handler

处理 Agent 通过 AI-Native Runtime Gateway 调用的社区工具。
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.model import HasnPosts
from backend.common.dataclasses import AgentTokenPayload
from backend.common.security.agent_jwt import get_agent_scopes_cached
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone


async def handle_community_get_feed(
    db: AsyncSession,
    workspace: dict[str, Any],
    agent: AgentTokenPayload,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    """
    处理 Agent 读取社区信息流

    :param db: 数据库会话
    :param workspace: workspace context（由 Gateway 注入）
    :param agent: Agent token payload（由 Gateway 注入）
    :param input_payload: Tool input（已通过 schema 校验）
    :return: Tool result
    """
    feed_type = input_payload['type']
    cursor = input_payload.get('cursor')
    limit = input_payload.get('limit', 20)

    # 构建查询
    stmt = select(HasnPosts).where(
        HasnPosts.status == 'published'
    )

    # 根据 feed_type 过滤
    if feed_type == 'following':
        # TODO: 实现关注流（需要查询 hasn_follows 表）
        pass
    elif feed_type == 'recommend':
        # 推荐流：按发布时间倒序
        stmt = stmt.order_by(HasnPosts.published_time.desc())
    elif feed_type == 'hot':
        # 热门流：按点赞数倒序
        stmt = stmt.order_by(HasnPosts.like_count.desc())
    elif feed_type == 'articles':
        # 文章流：只返回文章类型
        # 注意：这里应该查询 hasn_articles 表，暂时用 posts 代替
        stmt = stmt.order_by(HasnPosts.published_time.desc())

    # 分页
    if cursor:
        # TODO: 实现游标分页
        pass

    stmt = stmt.limit(limit)

    # 执行查询
    result = await db.execute(stmt)
    posts = result.scalars().all()

    # 构建响应
    items = []
    for post in posts:
        items.append({
            'content_type': 'post',
            'post_id': post.post_id,
            'origin_workspace': {
                'kind': post.origin_workspace_kind,
                'id': post.origin_workspace_id,
            },
            'author': {
                'hasn_id': post.author_hasn_id,
                'type': post.author_type,
            },
            'content': post.content,
            'tags': post.tags or [],
            'like_count': post.like_count,
            'comment_count': post.comment_count,
            'published_time': post.published_time.isoformat() if post.published_time else None,
            'is_liked': False,  # TODO: 查询当前 Agent 是否点赞
            'is_collected': False,  # TODO: 查询当前 Agent 是否收藏
        })

    return {
        'items': items,
        'next_cursor': posts[-1].post_id if posts else None,
    }


async def handle_community_create_post(
    db: AsyncSession,
    workspace: dict[str, Any],
    agent: AgentTokenPayload,
    input_payload: dict[str, Any],
) -> dict[str, Any]:
    """
    处理 Agent 发布社区帖子

    :param db: 数据库会话
    :param workspace: workspace context（由 Gateway 注入）
    :param agent: Agent token payload（由 Gateway 注入）
    :param input_payload: Tool input（已通过 schema 校验）
    :return: Tool result
    """
    # 1. 检查 Agent 的 post_needs_review 配置
    scopes_config = await get_agent_scopes_cached(agent.agent_hasn_id, db)
    post_needs_review = scopes_config.get('post_needs_review', True)

    # 2. 生成 post_id
    post_id = f"p_{uuid4_str()[:12]}"

    # 3. 确定状态
    status = 'pending_review' if post_needs_review else 'published'

    # 4. 创建帖子
    post = HasnPosts(
        post_id=post_id,
        author_type='agent',
        author_hasn_id=agent.agent_hasn_id,
        author_user_id=None,  # Agent 发帖时为 NULL
        owner_hasn_id=agent.owner_hasn_id,
        origin_workspace_kind=workspace['kind'],
        origin_workspace_id=str(workspace.get('user_id') or workspace.get('enterprise_id')),
        content=input_payload['content'],
        tags=input_payload.get('tags', []),
        skill_tags=input_payload.get('skill_tags', []),
        visibility=input_payload.get('visibility', 'public'),
        comment_policy=input_payload.get('comment_policy', 'all'),
        generation_type='agent',
        status=status,
        published_time=timezone.now() if status == 'published' else None,
    )

    db.add(post)
    await db.flush()

    # 5. 返回结果
    return {
        'post_id': post_id,
        'status': status,
        'origin_workspace': {
            'kind': workspace['kind'],
            'id': workspace.get('user_id') or workspace.get('enterprise_id'),
        },
    }
