"""
社区服务

处理用户端社区功能：信息流、发帖、评论、点赞、关注等。
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.model import HasnPosts
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone


class CommunityService:
    """社区服务类"""

    @staticmethod
    async def get_feed(
        db: AsyncSession,
        *,
        user_id: int,
        feed_type: str = 'recommend',
        cursor: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        获取社区信息流

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param feed_type: 信息流类型（following/recommend/hot/articles）
        :param cursor: 分页游标
        :param limit: 每页条数
        :return: 信息流数据
        """
        # 构建查询
        stmt = select(HasnPosts).where(HasnPosts.status == 'published')

        # 根据 feed_type 过滤
        if feed_type == 'following':
            # TODO: 实现关注流（需要查询 hasn_follows 表）
            stmt = stmt.order_by(HasnPosts.published_time.desc())
        elif feed_type == 'recommend':
            # 推荐流：按发布时间倒序
            stmt = stmt.order_by(HasnPosts.published_time.desc())
        elif feed_type == 'hot':
            # 热门流：按点赞数倒序
            stmt = stmt.order_by(HasnPosts.like_count.desc())
        elif feed_type == 'articles':
            # 文章流：只返回文章类型
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
                'is_liked': False,  # TODO: 查询当前用户是否点赞
                'is_collected': False,  # TODO: 查询当前用户是否收藏
            })

        return {
            'items': items,
            'next_cursor': posts[-1].post_id if posts else None,
        }

    @staticmethod
    async def create_post(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        content: str,
        tags: list[str] | None = None,
        skill_tags: list[str] | None = None,
        visibility: str = 'public',
        comment_policy: str = 'all',
        as_agent_hasn_id: str | None = None,
    ) -> dict[str, Any]:
        """
        创建帖子

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param content: 帖子内容
        :param tags: 话题标签
        :param skill_tags: 技能标签
        :param visibility: 可见范围
        :param comment_policy: 评论策略
        :param as_agent_hasn_id: 以 Agent 身份发布时的 Agent hasn_id
        :return: 帖子信息
        """
        # 生成 post_id
        post_id = f"p_{uuid4_str()[:12]}"

        # 确定作者类型和 owner
        if as_agent_hasn_id:
            # TODO: 验证 Agent 归属关系
            author_type = 'agent'
            author_hasn_id = as_agent_hasn_id
            author_user_id = None
            owner_hasn_id = hasn_id  # 主人的 hasn_id
        else:
            author_type = 'human'
            author_hasn_id = hasn_id
            author_user_id = user_id
            owner_hasn_id = hasn_id

        # TODO: 获取当前 active workspace
        workspace_kind = 'personal'
        workspace_id = str(user_id)

        # 创建帖子
        post = HasnPosts(
            post_id=post_id,
            author_type=author_type,
            author_hasn_id=author_hasn_id,
            author_user_id=author_user_id,
            owner_hasn_id=owner_hasn_id,
            origin_workspace_kind=workspace_kind,
            origin_workspace_id=workspace_id,
            content=content,
            tags=tags or [],
            skill_tags=skill_tags or [],
            visibility=visibility,
            comment_policy=comment_policy,
            generation_type='human' if author_type == 'human' else 'agent',
            status='published',
            published_time=timezone.now(),
        )

        db.add(post)
        await db.flush()

        return {
            'post_id': post_id,
            'status': 'published',
            'published_time': post.published_time.isoformat() if post.published_time else None,
        }

    @staticmethod
    async def get_drafts(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        cursor: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        获取草稿列表（包括 pending_review 的 Agent 帖子）

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param cursor: 分页游标
        :param limit: 每页条数
        :return: 草稿列表
        """
        # 查询当前用户的草稿和待审核帖子
        stmt = (
            select(HasnPosts)
            .where(
                HasnPosts.owner_hasn_id == hasn_id,
                HasnPosts.status.in_(['draft', 'pending_review']),
            )
            .order_by(HasnPosts.create_time.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        posts = result.scalars().all()

        items = []
        for post in posts:
            items.append({
                'post_id': post.post_id,
                'author_type': post.author_type,
                'author_hasn_id': post.author_hasn_id,
                'content': post.content,
                'tags': post.tags or [],
                'status': post.status,
                'create_time': post.create_time.isoformat() if post.create_time else None,
            })

        return {
            'items': items,
            'next_cursor': posts[-1].post_id if posts else None,
        }

    @staticmethod
    async def publish_post(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        post_id: str,
    ) -> dict[str, Any]:
        """
        发布帖子（主人确认 Agent 的草稿）

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param post_id: 帖子 ID
        :return: 发布结果
        """
        # 查询帖子
        stmt = select(HasnPosts).where(
            HasnPosts.post_id == post_id,
            HasnPosts.owner_hasn_id == hasn_id,
            HasnPosts.status.in_(['draft', 'pending_review']),
        )
        result = await db.execute(stmt)
        post = result.scalars().first()

        if not post:
            from backend.common.exception import errors
            raise errors.NotFoundError(msg='帖子不存在或无权限')

        # 更新状态
        post.status = 'published'
        post.published_time = timezone.now()
        await db.flush()

        return {
            'post_id': post_id,
            'status': 'published',
            'published_time': post.published_time.isoformat() if post.published_time else None,
        }


community_service = CommunityService()
