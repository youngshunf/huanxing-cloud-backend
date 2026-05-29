"""
社区服务

处理用户端社区功能：信息流、发帖、评论、点赞、关注等。
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from backend.app.hasn.model import HasnAgents, HasnHumans
from backend.app.hasn_community.model import HasnArticles, HasnCollectionItems, HasnCollections, HasnComments, HasnFollows, HasnLikes, HasnPosts
from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone


class CommunityService:
    """社区服务类"""

    @staticmethod
    async def get_feed(
        db: AsyncSession,
        *,
        user_id: int | None = None,
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
        # 创建别名用于 JOIN
        AuthorHuman = aliased(HasnHumans)
        AuthorAgent = aliased(HasnAgents)
        OwnerHuman = aliased(HasnHumans)

        # 构建查询，JOIN 用户信息表
        stmt = (
            select(
                HasnPosts,
                AuthorHuman.nickname.label('human_nickname'),
                AuthorHuman.avatar.label('human_avatar'),
                AuthorAgent.display_name.label('agent_display_name'),
                AuthorAgent.avatar.label('agent_avatar'),
                OwnerHuman.hasn_id.label('owner_hasn_id'),
                OwnerHuman.nickname.label('owner_nickname'),
            )
            .outerjoin(AuthorHuman, (HasnPosts.author_type == 'human') & (HasnPosts.author_hasn_id == AuthorHuman.hasn_id))
            .outerjoin(AuthorAgent, (HasnPosts.author_type == 'agent') & (HasnPosts.author_hasn_id == AuthorAgent.hasn_id))
            .outerjoin(OwnerHuman, (HasnPosts.author_type == 'agent') & (AuthorAgent.owner_id == OwnerHuman.hasn_id))
            .where(HasnPosts.status == 'published')
        )

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
        rows = result.all()

        # 构建响应
        items = []
        for row in rows:
            post = row.HasnPosts

            # 构建 author 信息
            author_info = {
                'hasn_id': post.author_hasn_id,
                'type': post.author_type,
            }

            if post.author_type == 'human':
                author_info['display_name'] = row.human_nickname or post.author_hasn_id
                author_info['avatar'] = row.human_avatar
            else:  # agent
                author_info['display_name'] = row.agent_display_name or post.author_hasn_id
                author_info['avatar'] = row.agent_avatar
                # 添加 owner 信息
                if row.owner_hasn_id:
                    author_info['owner'] = {
                        'hasn_id': row.owner_hasn_id,
                        'display_name': row.owner_nickname or row.owner_hasn_id,
                    }

            items.append({
                'content_type': 'post',
                'post_id': post.post_id,
                'origin_workspace': {
                    'kind': post.origin_workspace_kind,
                    'id': post.origin_workspace_id,
                },
                'author': author_info,
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
            'next_cursor': rows[-1].HasnPosts.post_id if rows else None,
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
    ) -> dict[str, Any]:
        """
        创建帖子（WebUI Owner JWT 通道：作者恒为操作者本人 human）

        身份模型见 docs/.../13-社区设计补丁 §1.5：WebUI 发帖永远是 human，
        Agent 自主发帖只走 MCP + Agent JWT（/api/v1/community/agent/*），
        不接受请求体身份字段，杜绝 as_agent_hasn_id 冒名越权。

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param content: 帖子内容
        :param tags: 话题标签
        :param skill_tags: 技能标签
        :param visibility: 可见范围
        :param comment_policy: 评论策略
        :return: 帖子信息
        """
        # 生成 post_id
        post_id = f"p_{uuid4_str()[:12]}"

        # 作者恒为当前 Owner JWT 对应的 human（身份 = 认证凭证，不接受请求体指定）
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
            generation_type='human',
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
            .order_by(HasnPosts.created_time.desc())
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
                'created_time': post.created_time.isoformat() if post.created_time else None,
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

    @staticmethod
    async def get_post(
        db: AsyncSession,
        *,
        post_id: str,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """
        获取帖子详情

        :param db: 数据库会话
        :param post_id: 帖子 ID
        :param user_id: 当前用户 ID
        :return: 帖子详情
        """
        # 创建别名用于 JOIN
        AuthorHuman = aliased(HasnHumans)
        AuthorAgent = aliased(HasnAgents)
        OwnerHuman = aliased(HasnHumans)

        # 构建查询，JOIN 用户信息表
        stmt = (
            select(
                HasnPosts,
                AuthorHuman.nickname.label('human_nickname'),
                AuthorHuman.avatar.label('human_avatar'),
                AuthorAgent.display_name.label('agent_display_name'),
                AuthorAgent.avatar.label('agent_avatar'),
                OwnerHuman.hasn_id.label('owner_hasn_id'),
                OwnerHuman.nickname.label('owner_nickname'),
            )
            .outerjoin(AuthorHuman, (HasnPosts.author_type == 'human') & (HasnPosts.author_hasn_id == AuthorHuman.hasn_id))
            .outerjoin(AuthorAgent, (HasnPosts.author_type == 'agent') & (HasnPosts.author_hasn_id == AuthorAgent.hasn_id))
            .outerjoin(OwnerHuman, (HasnPosts.author_type == 'agent') & (AuthorAgent.owner_id == OwnerHuman.hasn_id))
            .where(HasnPosts.post_id == post_id, HasnPosts.status == 'published')
        )

        result = await db.execute(stmt)
        row = result.first()

        if not row:
            from backend.common.exception import errors
            raise errors.NotFoundError(msg='帖子不存在')

        post = row.HasnPosts

        # 构建 author 信息
        author_info = {
            'hasn_id': post.author_hasn_id,
            'type': post.author_type,
        }

        if post.author_type == 'human':
            author_info['display_name'] = row.human_nickname or post.author_hasn_id
            author_info['avatar'] = row.human_avatar
        else:  # agent
            author_info['display_name'] = row.agent_display_name or post.author_hasn_id
            author_info['avatar'] = row.agent_avatar
            # 添加 owner 信息
            if row.owner_hasn_id:
                author_info['owner'] = {
                    'hasn_id': row.owner_hasn_id,
                    'display_name': row.owner_nickname or row.owner_hasn_id,
                }

        return {
            'content_type': 'post',
            'post_id': post.post_id,
            'origin_workspace': {
                'kind': post.origin_workspace_kind,
                'id': post.origin_workspace_id,
            },
            'author': author_info,
            'content': post.content,
            'tags': post.tags or [],
            'like_count': post.like_count,
            'comment_count': post.comment_count,
            'published_time': post.published_time.isoformat() if post.published_time else None,
            'is_liked': False,  # TODO: 查询当前用户是否点赞
            'is_collected': False,  # TODO: 查询当前用户是否收藏
        }

    @staticmethod
    async def get_agent_post_resource(
        db: AsyncSession,
        *,
        agent: AgentTokenPayload,
        post_id: str,
    ) -> dict[str, Any]:
        stmt = select(HasnPosts).where(
            HasnPosts.post_id == post_id,
            HasnPosts.status == 'published',
        )
        result = await db.execute(stmt)
        post = result.scalar_one_or_none()
        if not post:
            raise errors.NotFoundError(msg='帖子不存在')
        CommunityService._assert_agent_can_read_community_resource(agent=agent, resource=post)
        summary = _safe_summary(post.content)
        return {
            'resource': {
                'type': 'community.post',
                'id': post.post_id,
                'app_id': 'community',
                'uri': f'hasn://app/community/posts/{post.post_id}',
            },
            'summary': summary,
            'content': post.content,
            'author': {
                'hasn_id': post.author_hasn_id,
                'type': post.author_type,
                'owner_hasn_id': post.owner_hasn_id,
            },
            'origin_workspace': {
                'kind': post.origin_workspace_kind,
                'id': post.origin_workspace_id,
            },
            'published_time': post.published_time.isoformat() if post.published_time else None,
        }

    # ==================== 评论功能 ====================

    @staticmethod
    async def get_comments(
        db: AsyncSession,
        *,
        target_type: str,
        target_id: str,
        sort: str = 'time_desc',
        user_id: int | None = None,
        cursor: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        获取评论列表

        :param db: 数据库会话
        :param target_type: 目标类型（post/article）
        :param target_id: 目标 ID
        :param sort: 排序方式（time_asc/time_desc/hot）
        :param user_id: 当前用户 ID
        :param cursor: 分页游标
        :param limit: 每页条数
        :return: 评论列表
        """
        # 创建别名用于 JOIN
        AuthorHuman = aliased(HasnHumans)
        AuthorAgent = aliased(HasnAgents)
        OwnerHuman = aliased(HasnHumans)

        # 构建查询，JOIN 用户信息表
        stmt = (
            select(
                HasnComments,
                AuthorHuman.nickname.label('human_nickname'),
                AuthorHuman.avatar.label('human_avatar'),
                AuthorAgent.display_name.label('agent_display_name'),
                AuthorAgent.avatar.label('agent_avatar'),
                OwnerHuman.hasn_id.label('owner_hasn_id'),
                OwnerHuman.nickname.label('owner_nickname'),
            )
            .outerjoin(AuthorHuman, (HasnComments.author_type == 'human') & (HasnComments.author_hasn_id == AuthorHuman.hasn_id))
            .outerjoin(AuthorAgent, (HasnComments.author_type == 'agent') & (HasnComments.author_hasn_id == AuthorAgent.hasn_id))
            .outerjoin(OwnerHuman, (HasnComments.author_type == 'agent') & (AuthorAgent.owner_id == OwnerHuman.hasn_id))
            .where(
                HasnComments.target_type == target_type,
                HasnComments.target_id == target_id,
                HasnComments.status == 'visible',
            )
        )

        # 排序
        if sort == 'time_asc':
            stmt = stmt.order_by(HasnComments.created_time.asc())
        elif sort == 'time_desc':
            stmt = stmt.order_by(HasnComments.created_time.desc())
        elif sort == 'hot':
            stmt = stmt.order_by(HasnComments.like_count.desc())

        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        rows = result.all()

        items = []
        for row in rows:
            comment = row.HasnComments

            # 构建 author 信息
            author_info = {
                'hasn_id': comment.author_hasn_id,
                'type': comment.author_type,
            }

            if comment.author_type == 'human':
                author_info['display_name'] = row.human_nickname or comment.author_hasn_id
                author_info['avatar'] = row.human_avatar
            else:  # agent
                author_info['display_name'] = row.agent_display_name or comment.author_hasn_id
                author_info['avatar'] = row.agent_avatar
                # 添加 owner 信息
                if row.owner_hasn_id:
                    author_info['owner'] = {
                        'hasn_id': row.owner_hasn_id,
                        'display_name': row.owner_nickname or row.owner_hasn_id,
                    }

            items.append({
                'comment_id': comment.comment_id,
                'author': author_info,
                'content': comment.content,
                'parent_id': comment.parent_id,
                'like_count': comment.like_count,
                'created_time': comment.created_time.isoformat() if comment.created_time else None,
            })

        return {
            'items': items,
            'next_cursor': rows[-1].HasnComments.comment_id if rows else None,
        }

    @staticmethod
    async def create_comment(
        db: AsyncSession,
        *,
        target_type: str,
        target_id: str,
        user_id: int,
        hasn_id: str,
        content: str,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        """
        创建评论

        :param db: 数据库会话
        :param target_type: 目标类型（post/article）
        :param target_id: 目标 ID
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param content: 评论内容
        :param parent_id: 父评论 ID（楼中楼回复）
        :return: 评论信息
        """
        comment_id = f"cmt_{uuid4_str()[:12]}"

        # 确定 root_id
        root_id = None
        if parent_id:
            # 查询父评论
            parent_stmt = select(HasnComments).where(HasnComments.comment_id == parent_id)
            parent_result = await db.execute(parent_stmt)
            parent_comment = parent_result.scalars().first()
            if parent_comment:
                root_id = parent_comment.root_id or parent_comment.comment_id

        # TODO: 获取当前 active workspace
        workspace_kind = 'personal'
        workspace_id = str(user_id)

        comment = HasnComments(
            comment_id=comment_id,
            target_type=target_type,
            target_id=target_id,
            parent_id=parent_id,
            root_id=root_id,
            author_type='human',
            author_hasn_id=hasn_id,
            author_user_id=user_id,
            owner_hasn_id=hasn_id,
            origin_workspace_kind=workspace_kind,
            origin_workspace_id=workspace_id,
            content=content,
            status='visible',
        )

        db.add(comment)
        await db.flush()

        # 更新目标的评论计数
        if target_type == 'post':
            post_stmt = select(HasnPosts).where(HasnPosts.post_id == target_id)
            post_result = await db.execute(post_stmt)
            post = post_result.scalars().first()
            if post:
                post.comment_count += 1
        elif target_type == 'article':
            article_stmt = select(HasnArticles).where(HasnArticles.article_id == target_id)
            article_result = await db.execute(article_stmt)
            article = article_result.scalars().first()
            if article:
                article.comment_count += 1

        await db.flush()

        return {
            'comment_id': comment_id,
            'status': 'visible',
            'created_time': comment.created_time.isoformat() if comment.created_time else None,
        }

    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        *,
        comment_id: str,
        user_id: int,
        hasn_id: str,
    ) -> None:
        """
        删除评论

        :param db: 数据库会话
        :param comment_id: 评论 ID
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        """
        stmt = select(HasnComments).where(
            HasnComments.comment_id == comment_id,
            HasnComments.owner_hasn_id == hasn_id,
        )
        result = await db.execute(stmt)
        comment = result.scalars().first()

        if not comment:
            from backend.common.exception import errors

            raise errors.NotFoundError(msg='评论不存在或无权限')

        comment.status = 'deleted'
        await db.flush()

    # ==================== 点赞功能 ====================

    @staticmethod
    async def create_like(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        target_type: str,
        target_id: str,
    ) -> None:
        """
        点赞

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param target_type: 目标类型（post/article/comment）
        :param target_id: 目标 ID
        """
        # 检查是否已点赞
        check_stmt = select(HasnLikes).where(
            HasnLikes.user_hasn_id == hasn_id,
            HasnLikes.target_type == target_type,
            HasnLikes.target_id == target_id,
        )
        check_result = await db.execute(check_stmt)
        existing = check_result.scalars().first()

        if existing:
            return  # 已点赞，直接返回

        # 创建点赞记录
        like = HasnLikes(
            user_hasn_id=hasn_id,
            target_type=target_type,
            target_id=target_id,
        )
        db.add(like)

        # 更新目标的点赞计数
        if target_type == 'post':
            post_stmt = select(HasnPosts).where(HasnPosts.post_id == target_id)
            post_result = await db.execute(post_stmt)
            post = post_result.scalars().first()
            if post:
                post.like_count += 1
        elif target_type == 'article':
            article_stmt = select(HasnArticles).where(HasnArticles.article_id == target_id)
            article_result = await db.execute(article_stmt)
            article = article_result.scalars().first()
            if article:
                article.like_count += 1
        elif target_type == 'comment':
            comment_stmt = select(HasnComments).where(HasnComments.comment_id == target_id)
            comment_result = await db.execute(comment_stmt)
            comment = comment_result.scalars().first()
            if comment:
                comment.like_count += 1

        await db.flush()

    @staticmethod
    async def delete_like(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        target_type: str,
        target_id: str,
    ) -> None:
        """
        取消点赞

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param target_type: 目标类型（post/article/comment）
        :param target_id: 目标 ID
        """
        stmt = select(HasnLikes).where(
            HasnLikes.user_hasn_id == hasn_id,
            HasnLikes.target_type == target_type,
            HasnLikes.target_id == target_id,
        )
        result = await db.execute(stmt)
        like = result.scalars().first()

        if not like:
            return  # 未点赞，直接返回

        await db.delete(like)

        # 更新目标的点赞计数
        if target_type == 'post':
            post_stmt = select(HasnPosts).where(HasnPosts.post_id == target_id)
            post_result = await db.execute(post_stmt)
            post = post_result.scalars().first()
            if post:
                post.like_count = max(0, post.like_count - 1)
        elif target_type == 'article':
            article_stmt = select(HasnArticles).where(HasnArticles.article_id == target_id)
            article_result = await db.execute(article_stmt)
            article = article_result.scalars().first()
            if article:
                article.like_count = max(0, article.like_count - 1)
        elif target_type == 'comment':
            comment_stmt = select(HasnComments).where(HasnComments.comment_id == target_id)
            comment_result = await db.execute(comment_stmt)
            comment = comment_result.scalars().first()
            if comment:
                comment.like_count = max(0, comment.like_count - 1)

        await db.flush()

    # ==================== 关注功能 ====================

    @staticmethod
    async def create_follow(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        target_type: str,
        target_hasn_id: str,
    ) -> None:
        """
        关注

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param target_type: 目标类型（human/agent/topic）
        :param target_hasn_id: 目标 hasn_id
        """
        # 检查是否已关注
        check_stmt = select(HasnFollows).where(
            HasnFollows.follower_hasn_id == hasn_id,
            HasnFollows.target_type == target_type,
            HasnFollows.target_hasn_id == target_hasn_id,
        )
        check_result = await db.execute(check_stmt)
        existing = check_result.scalars().first()

        if existing:
            return  # 已关注，直接返回

        # 创建关注记录
        follow = HasnFollows(
            follower_hasn_id=hasn_id,
            target_type=target_type,
            target_hasn_id=target_hasn_id,
        )
        db.add(follow)
        await db.flush()

    @staticmethod
    async def delete_follow(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        target_type: str,
        target_hasn_id: str,
    ) -> None:
        """
        取消关注

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param target_type: 目标类型（human/agent/topic）
        :param target_hasn_id: 目标 hasn_id
        """
        stmt = select(HasnFollows).where(
            HasnFollows.follower_hasn_id == hasn_id,
            HasnFollows.target_type == target_type,
            HasnFollows.target_hasn_id == target_hasn_id,
        )
        result = await db.execute(stmt)
        follow = result.scalars().first()

        if not follow:
            return  # 未关注，直接返回

        await db.delete(follow)
        await db.flush()

    # ==================== 主页功能 ====================

    @staticmethod
    async def get_profile(
        db: AsyncSession,
        *,
        hasn_id: str,
        viewer_user_id: int,
    ) -> dict[str, Any]:
        """
        获取主页信息

        :param db: 数据库会话
        :param hasn_id: 目标 hasn_id
        :param viewer_user_id: 查看者用户 ID
        :return: 主页信息
        """
        # TODO: 实现完整的主页信息查询
        # 需要查询 hasn_humans 或 hasn_agents 表
        # 需要统计关注数、粉丝数、帖子数等
        return {
            'hasn_id': hasn_id,
            'type': 'human',  # TODO: 判断类型
            'display_name': 'User',
            'bio': '',
            'avatar': '',
            'follower_count': 0,
            'following_count': 0,
            'post_count': 0,
            'is_following': False,
        }

    @staticmethod
    async def get_profile_posts(
        db: AsyncSession,
        *,
        hasn_id: str,
        viewer_user_id: int,
        cursor: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        获取主页帖子列表

        :param db: 数据库会话
        :param hasn_id: 目标 hasn_id
        :param viewer_user_id: 查看者用户 ID
        :param cursor: 分页游标
        :param limit: 每页条数
        :return: 帖子列表
        """
        stmt = (
            select(HasnPosts)
            .where(
                HasnPosts.author_hasn_id == hasn_id,
                HasnPosts.status == 'published',
            )
            .order_by(HasnPosts.published_time.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        posts = result.scalars().all()

        items = []
        for post in posts:
            items.append({
                'post_id': post.post_id,
                'content': post.content,
                'tags': post.tags or [],
                'like_count': post.like_count,
                'comment_count': post.comment_count,
                'published_time': post.published_time.isoformat() if post.published_time else None,
            })

        return {
            'items': items,
            'next_cursor': posts[-1].post_id if posts else None,
        }

    @staticmethod
    async def get_profile_articles(
        db: AsyncSession,
        *,
        hasn_id: str,
        viewer_user_id: int,
        cursor: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        获取主页文章列表

        :param db: 数据库会话
        :param hasn_id: 目标 hasn_id
        :param viewer_user_id: 查看者用户 ID
        :param cursor: 分页游标
        :param limit: 每页条数
        :return: 文章列表
        """
        stmt = (
            select(HasnArticles)
            .where(
                HasnArticles.author_hasn_id == hasn_id,
                HasnArticles.status == 'published',
            )
            .order_by(HasnArticles.published_time.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        articles = result.scalars().all()

        items = []
        for article in articles:
            items.append({
                'article_id': article.article_id,
                'title': article.title,
                'summary': article.summary,
                'cover_url': article.cover_url,
                'tags': article.tags or [],
                'like_count': article.like_count,
                'comment_count': article.comment_count,
                'published_time': article.published_time.isoformat() if article.published_time else None,
            })

        return {
            'items': items,
            'next_cursor': articles[-1].article_id if articles else None,
        }

    @staticmethod
    async def get_profile_agents(
        db: AsyncSession,
        *,
        hasn_id: str,
        viewer_user_id: int,
    ) -> list[dict[str, Any]]:
        """
        获取主页拥有的 Agent 列表

        :param db: 数据库会话
        :param hasn_id: 目标 hasn_id
        :param viewer_user_id: 查看者用户 ID
        :return: Agent 列表
        """
        # 查询该用户拥有的 Agent
        stmt = (
            select(HasnAgents)
            .where(HasnAgents.owner_id == hasn_id)
            .order_by(HasnAgents.follower_count.desc())
        )

        result = await db.execute(stmt)
        agents = result.scalars().all()

        # 查询当前用户是否已关注这些 Agent
        from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

        viewer_human = await hasn_humans_dao.get_by_user_id(db, viewer_user_id)
        viewer_hasn_id = viewer_human.hasn_id if viewer_human else None

        agent_list = []
        for agent in agents:
            # 检查是否已关注
            is_following = False
            if viewer_hasn_id:
                follow_stmt = select(HasnFollows).where(
                    HasnFollows.follower_hasn_id == viewer_hasn_id,
                    HasnFollows.target_type == 'agent',
                    HasnFollows.target_hasn_id == agent.hasn_id,
                )
                follow_result = await db.execute(follow_stmt)
                is_following = follow_result.scalars().first() is not None

            agent_list.append({
                'hasn_id': agent.hasn_id,
                'display_name': agent.display_name,
                'bio': agent.bio or '',
                'avatar': agent.avatar,
                'owner': {
                    'hasn_id': hasn_id,
                    'display_name': hasn_id,  # TODO: 查询 owner 的 display_name
                },
                'follower_count': agent.follower_count,
                'is_following': is_following,
            })

        return agent_list

    @staticmethod
    async def get_profile_collections(
        db: AsyncSession,
        *,
        hasn_id: str,
        viewer_user_id: int,
    ) -> list[dict[str, Any]]:
        """
        获取主页公开收藏夹列表

        :param db: 数据库会话
        :param hasn_id: 目标 hasn_id
        :param viewer_user_id: 查看者用户 ID
        :return: 收藏夹列表
        """
        # 查询公开收藏夹
        stmt = (
            select(HasnCollections)
            .where(
                HasnCollections.owner_hasn_id == hasn_id,
                HasnCollections.is_public == True,  # noqa: E712
            )
            .order_by(HasnCollections.created_time.desc())
        )

        result = await db.execute(stmt)
        collections = result.scalars().all()

        collection_list = []
        for collection in collections:
            # 统计收藏项数量
            count_stmt = select(HasnCollectionItems).where(
                HasnCollectionItems.collection_id == collection.collection_id
            )
            count_result = await db.execute(count_stmt)
            item_count = len(count_result.scalars().all())

            collection_list.append({
                'collection_id': collection.collection_id,
                'name': collection.name,
                'description': collection.description,
                'is_public': collection.is_public,
                'item_count': item_count,
            })

        return collection_list

    # ==================== 热门话题 ====================

    @staticmethod
    async def get_trending_topics(
        db: AsyncSession,
        *,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        获取热门话题

        :param db: 数据库会话
        :param limit: 返回数量
        :return: 热门话题列表
        """
        # TODO: 实现真实的热门话题统计
        # 当前返回模拟数据
        return [
            {'topic': 'AI分身产品设计', 'post_count': 128, 'trend': 'rising'},
            {'topic': 'Agent工作流', 'post_count': 96, 'trend': 'stable'},
            {'topic': 'HASN社区', 'post_count': 84, 'trend': 'rising'},
            {'topic': '产品设计', 'post_count': 72, 'trend': 'stable'},
            {'topic': '技术架构', 'post_count': 58, 'trend': 'falling'},
        ][:limit]

    # ==================== 推荐 Agent ====================

    @staticmethod
    async def get_recommended_agents(
        db: AsyncSession,
        *,
        viewer_user_id: int,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """
        获取推荐 Agent

        :param db: 数据库会话
        :param viewer_user_id: 查看者用户 ID
        :param limit: 返回数量
        :return: 推荐 Agent 列表
        """
        # 查询活跃的 Agent（按粉丝数排序）
        OwnerHuman = aliased(HasnHumans)

        stmt = (
            select(
                HasnAgents,
                OwnerHuman.hasn_id.label('owner_hasn_id'),
                OwnerHuman.nickname.label('owner_nickname'),
            )
            .join(OwnerHuman, HasnAgents.owner_id == OwnerHuman.hasn_id)
            .where(HasnAgents.hasn_social_enabled == True)  # noqa: E712
            .order_by(HasnAgents.follower_count.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        # 查询当前用户是否已关注这些 Agent
        from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

        viewer_human = await hasn_humans_dao.get_by_user_id(db, viewer_user_id)
        viewer_hasn_id = viewer_human.hasn_id if viewer_human else None

        agents = []
        for row in rows:
            agent = row.HasnAgents

            # 检查是否已关注
            is_following = False
            if viewer_hasn_id:
                follow_stmt = select(HasnFollows).where(
                    HasnFollows.follower_hasn_id == viewer_hasn_id,
                    HasnFollows.target_type == 'agent',
                    HasnFollows.target_hasn_id == agent.hasn_id,
                )
                follow_result = await db.execute(follow_stmt)
                is_following = follow_result.scalars().first() is not None

            agents.append({
                'hasn_id': agent.hasn_id,
                'display_name': agent.display_name,
                'bio': agent.bio or '',
                'avatar': agent.avatar,
                'owner': {
                    'hasn_id': row.owner_hasn_id,
                    'display_name': row.owner_nickname or row.owner_hasn_id,
                },
                'follower_count': agent.follower_count,
                'is_following': is_following,
            })

        return agents

    # ==================== 待确认草稿 ====================

    @staticmethod
    async def get_pending_drafts(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        cursor: str | None = None,
        limit: int = 3,
    ) -> dict[str, Any]:
        """
        获取待确认草稿（需要主人确认的 Agent 草稿）

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param cursor: 分页游标
        :param limit: 每页条数
        :return: 待确认草稿列表
        """
        # 查询当前用户拥有的 Agent
        agent_stmt = select(HasnAgents.hasn_id).where(HasnAgents.owner_id == hasn_id)
        agent_result = await db.execute(agent_stmt)
        agent_ids = [row[0] for row in agent_result.all()]

        if not agent_ids:
            return {'items': [], 'next_cursor': None}

        # 查询这些 Agent 的待确认草稿
        AuthorAgent = aliased(HasnAgents)

        stmt = (
            select(
                HasnPosts,
                AuthorAgent.display_name.label('agent_display_name'),
            )
            .join(AuthorAgent, HasnPosts.author_hasn_id == AuthorAgent.hasn_id)
            .where(
                HasnPosts.author_type == 'agent',
                HasnPosts.author_hasn_id.in_(agent_ids),
                HasnPosts.status == 'pending_review',
            )
            .order_by(HasnPosts.created_time.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        items = []
        for row in rows:
            post = row.HasnPosts

            items.append({
                'content_type': 'post',
                'post_id': post.post_id,
                'origin_workspace': {
                    'kind': post.origin_workspace_kind,
                    'id': post.origin_workspace_id,
                },
                'author': {
                    'hasn_id': post.author_hasn_id,
                    'type': 'agent',
                    'display_name': row.agent_display_name or post.author_hasn_id,
                },
                'content': post.content,
                'tags': post.tags or [],
                'like_count': post.like_count,
                'comment_count': post.comment_count,
                'published_time': post.created_time.isoformat() if post.created_time else None,
                'is_liked': False,
                'is_collected': False,
            })

        return {
            'items': items,
            'next_cursor': rows[-1].HasnPosts.post_id if rows else None,
        }

    # ==================== 文章相关方法 ====================

    @staticmethod
    async def create_article(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        title: str,
        content: str,
        summary: str | None = None,
        cover_url: str | None = None,
        tags: list[str] | None = None,
        visibility: str = 'public',
        comment_policy: str = 'all',
    ) -> dict[str, Any]:
        """
        创建文章（WebUI Owner JWT 通道：作者恒为操作者本人 human）

        身份模型见 docs/.../13-社区设计补丁 §1.5：WebUI 发文永远是 human，
        Agent 自主发文只走 MCP + Agent JWT（/api/v1/community/agent/*），
        不接受请求体身份字段，杜绝 as_agent_hasn_id 冒名越权。

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param title: 文章标题
        :param content: 文章内容（Markdown）
        :param summary: 文章摘要
        :param cover_url: 封面图片 URL
        :param tags: 话题标签
        :param visibility: 可见范围
        :param comment_policy: 评论策略
        :return: 文章信息
        """
        from backend.app.hasn_community.model.hasn_articles import HasnArticles

        # 生成 article_id
        article_id = f"art_{uuid4_str()[:12]}"

        # 作者恒为当前 Owner JWT 对应的 human（身份 = 认证凭证，不接受请求体指定）
        author_type = 'human'
        author_hasn_id = hasn_id
        author_user_id = user_id
        owner_hasn_id = hasn_id

        # TODO: 获取当前 active workspace
        workspace_kind = 'personal'
        workspace_id = str(user_id)

        # 创建文章
        article = HasnArticles(
            article_id=article_id,
            author_type=author_type,
            author_hasn_id=author_hasn_id,
            author_user_id=author_user_id,
            owner_hasn_id=owner_hasn_id,
            origin_workspace_kind=workspace_kind,
            origin_workspace_id=workspace_id,
            title=title,
            summary=summary,
            cover_url=cover_url,
            content=content,
            tags=tags or [],
            visibility=visibility,
            comment_policy=comment_policy,
            generation_type='human',
            status='published',
            published_time=timezone.now(),
        )

        db.add(article)
        await db.flush()

        return {
            'article_id': article_id,
            'status': 'published',
            'published_time': article.published_time.isoformat() if article.published_time else None,
        }

    @staticmethod
    async def get_article(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        article_id: str,
    ) -> dict[str, Any]:
        """
        获取文章详情

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param article_id: 文章 ID
        :return: 文章详情
        """
        from backend.app.hasn_community.model.hasn_articles import HasnArticles
        from backend.app.hasn.model.hasn_humans import HasnHumans
        from backend.app.hasn.model.hasn_agents import HasnAgents

        # 查询文章
        stmt = select(HasnArticles).where(HasnArticles.article_id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()

        if not article:
            from backend.common.exception import errors

            raise errors.NotFoundError(msg='文章不存在')

        # 查询作者信息
        author_info = {'hasn_id': article.author_hasn_id, 'type': article.author_type}

        if article.author_type == 'human':
            stmt = select(HasnHumans).where(HasnHumans.hasn_id == article.author_hasn_id)
            result = await db.execute(stmt)
            human = result.scalar_one_or_none()
            if human:
                author_info['display_name'] = human.nickname
                author_info['avatar'] = human.avatar
        else:
            stmt = select(HasnAgents).where(HasnAgents.hasn_id == article.author_hasn_id)
            result = await db.execute(stmt)
            agent = result.scalar_one_or_none()
            if agent:
                author_info['display_name'] = agent.display_name
                author_info['avatar'] = agent.avatar

                # 查询 Agent 的主人信息
                stmt = select(HasnHumans).where(HasnHumans.hasn_id == agent.owner_hasn_id)
                result = await db.execute(stmt)
                owner = result.scalar_one_or_none()
                if owner:
                    author_info['owner'] = {
                        'hasn_id': owner.hasn_id,
                        'display_name': owner.nickname,
                    }

        # TODO: 查询点赞和收藏状态
        is_liked = False
        is_collected = False

        return {
            'article_id': article.article_id,
            'title': article.title,
            'summary': article.summary,
            'cover_url': article.cover_url,
            'content': article.content,
            'author': author_info,
            'tags': article.tags or [],
            'visibility': article.visibility,
            'comment_policy': article.comment_policy,
            'like_count': article.like_count,
            'comment_count': article.comment_count,
            'view_count': article.view_count,
            'published_time': article.published_time.isoformat() if article.published_time else None,
            'updated_time': article.updated_time.isoformat() if article.updated_time else None,
            'is_liked': is_liked,
            'is_collected': is_collected,
        }

    @staticmethod
    async def get_agent_article_resource(
        db: AsyncSession,
        *,
        agent: AgentTokenPayload,
        article_id: str,
    ) -> dict[str, Any]:
        stmt = select(HasnArticles).where(
            HasnArticles.article_id == article_id,
            HasnArticles.status == 'published',
        )
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()
        if not article:
            raise errors.NotFoundError(msg='文章不存在')
        CommunityService._assert_agent_can_read_community_resource(agent=agent, resource=article)
        return {
            'resource': {
                'type': 'community.article',
                'id': article.article_id,
                'app_id': 'community',
                'uri': f'hasn://app/community/articles/{article.article_id}',
            },
            'summary': article.summary or _safe_summary(article.content),
            'content': article.content,
            'title': article.title,
            'author': {
                'hasn_id': article.author_hasn_id,
                'type': article.author_type,
                'owner_hasn_id': article.owner_hasn_id,
            },
            'origin_workspace': {
                'kind': article.origin_workspace_kind,
                'id': article.origin_workspace_id,
            },
            'published_time': article.published_time.isoformat() if article.published_time else None,
        }

    @staticmethod
    def _assert_agent_can_read_community_resource(*, agent: AgentTokenPayload, resource: Any) -> None:
        visibility = getattr(resource, 'visibility', 'public')
        if visibility == 'public':
            return
        owner_hasn_id = getattr(resource, 'owner_hasn_id', None)
        author_hasn_id = getattr(resource, 'author_hasn_id', None)
        if agent.owner_hasn_id in {owner_hasn_id, author_hasn_id}:
            return
        raise errors.ForbiddenError(msg='社区资源不可见')

    @staticmethod
    async def update_article(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        article_id: str,
        title: str | None = None,
        summary: str | None = None,
        cover_url: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
        visibility: str | None = None,
        comment_policy: str | None = None,
    ) -> dict[str, Any]:
        """
        更新文章

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param article_id: 文章 ID
        :param title: 文章标题
        :param summary: 文章摘要
        :param cover_url: 封面图片 URL
        :param content: 文章内容
        :param tags: 话题标签
        :param visibility: 可见范围
        :param comment_policy: 评论策略
        :return: 更新结果
        """
        from backend.app.hasn_community.model.hasn_articles import HasnArticles

        # 查询文章
        stmt = select(HasnArticles).where(HasnArticles.article_id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()

        if not article:
            from backend.common.exception import errors

            raise errors.NotFoundError(msg='文章不存在')

        # 验证权限（只有作者或主人可以编辑）
        if article.author_hasn_id != hasn_id and article.owner_hasn_id != hasn_id:
            from backend.common.exception import errors

            raise errors.ForbiddenError(msg='无权编辑此文章')

        # 更新字段
        if title is not None:
            article.title = title
        if summary is not None:
            article.summary = summary
        if cover_url is not None:
            article.cover_url = cover_url
        if content is not None:
            article.content = content
        if tags is not None:
            article.tags = tags
        if visibility is not None:
            article.visibility = visibility
        if comment_policy is not None:
            article.comment_policy = comment_policy

        article.updated_time = timezone.now()

        await db.flush()

        return {
            'article_id': article_id,
            'status': 'published',
            'updated_time': article.updated_time.isoformat() if article.updated_time else None,
        }

    @staticmethod
    async def delete_article(
        db: AsyncSession,
        *,
        user_id: int,
        hasn_id: str,
        article_id: str,
    ) -> dict[str, Any]:
        """
        删除文章

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param hasn_id: 用户的 hasn_id
        :param article_id: 文章 ID
        :return: 删除结果
        """
        from backend.app.hasn_community.model.hasn_articles import HasnArticles

        # 查询文章
        stmt = select(HasnArticles).where(HasnArticles.article_id == article_id)
        result = await db.execute(stmt)
        article = result.scalar_one_or_none()

        if not article:
            from backend.common.exception import errors

            raise errors.NotFoundError(msg='文章不存在')

        # 验证权限（只有作者或主人可以删除）
        if article.author_hasn_id != hasn_id and article.owner_hasn_id != hasn_id:
            from backend.common.exception import errors

            raise errors.ForbiddenError(msg='无权删除此文章')

        # 软删除
        article.status = 'deleted'
        article.updated_time = timezone.now()

        await db.flush()

        return {
            'article_id': article_id,
            'status': 'deleted',
        }

    @staticmethod
    async def get_public_article(
        db: AsyncSession,
        *,
        article_id: str,
    ) -> dict[str, Any]:
        """公开（匿名）获取文章详情：仅 status=published 且 visibility=public。

        供 open scope 使用，不接受查看者身份，不做个性化（is_liked/is_collected）。
        """
        stmt = select(HasnArticles).where(
            HasnArticles.article_id == article_id,
            HasnArticles.status == 'published',
            HasnArticles.visibility == 'public',
        )
        article = (await db.execute(stmt)).scalar_one_or_none()
        if not article:
            raise errors.NotFoundError(msg='文章不存在')

        author_info: dict[str, Any] = {'hasn_id': article.author_hasn_id, 'type': article.author_type}
        if article.author_type == 'human':
            human = (
                await db.execute(select(HasnHumans).where(HasnHumans.hasn_id == article.author_hasn_id))
            ).scalar_one_or_none()
            if human:
                author_info['display_name'] = human.nickname
                author_info['avatar'] = human.avatar
        else:
            agent = (
                await db.execute(select(HasnAgents).where(HasnAgents.hasn_id == article.author_hasn_id))
            ).scalar_one_or_none()
            if agent:
                author_info['display_name'] = agent.display_name
                author_info['avatar'] = agent.avatar
                owner = (
                    await db.execute(select(HasnHumans).where(HasnHumans.hasn_id == agent.owner_hasn_id))
                ).scalar_one_or_none()
                if owner:
                    author_info['owner'] = {'hasn_id': owner.hasn_id, 'display_name': owner.nickname}

        return {
            'article_id': article.article_id,
            'title': article.title,
            'summary': article.summary,
            'cover_url': article.cover_url,
            'content': article.content,
            'author': author_info,
            'tags': article.tags or [],
            'visibility': article.visibility,
            'comment_policy': article.comment_policy,
            'like_count': article.like_count,
            'comment_count': article.comment_count,
            'view_count': article.view_count,
            'published_time': article.published_time.isoformat() if article.published_time else None,
            'updated_time': article.updated_time.isoformat() if article.updated_time else None,
        }

    # ==================== 管理端（只读审核可见性） ====================

    @staticmethod
    async def admin_list_posts(
        db: AsyncSession,
        *,
        status: str | None = None,
        author_hasn_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """管理端列出帖子（全状态，可按 status/author 过滤），用于审核可见性。"""
        AuthorHuman = aliased(HasnHumans)
        AuthorAgent = aliased(HasnAgents)
        stmt = (
            select(
                HasnPosts,
                AuthorHuman.nickname.label('human_nickname'),
                AuthorAgent.display_name.label('agent_display_name'),
            )
            .outerjoin(AuthorHuman, (HasnPosts.author_type == 'human') & (HasnPosts.author_hasn_id == AuthorHuman.hasn_id))
            .outerjoin(AuthorAgent, (HasnPosts.author_type == 'agent') & (HasnPosts.author_hasn_id == AuthorAgent.hasn_id))
        )
        if status:
            stmt = stmt.where(HasnPosts.status == status)
        if author_hasn_id:
            stmt = stmt.where(HasnPosts.author_hasn_id == author_hasn_id)
        stmt = stmt.order_by(HasnPosts.created_time.desc()).limit(limit).offset(offset)
        rows = (await db.execute(stmt)).all()
        items = [
            {
                'post_id': r.HasnPosts.post_id,
                'author': {
                    'hasn_id': r.HasnPosts.author_hasn_id,
                    'type': r.HasnPosts.author_type,
                    'display_name': (r.human_nickname if r.HasnPosts.author_type == 'human' else r.agent_display_name)
                    or r.HasnPosts.author_hasn_id,
                },
                'owner_hasn_id': r.HasnPosts.owner_hasn_id,
                'content': r.HasnPosts.content,
                'tags': r.HasnPosts.tags or [],
                'visibility': r.HasnPosts.visibility,
                'status': r.HasnPosts.status,
                'generation_type': r.HasnPosts.generation_type,
                'like_count': r.HasnPosts.like_count,
                'comment_count': r.HasnPosts.comment_count,
                'created_time': r.HasnPosts.created_time.isoformat() if r.HasnPosts.created_time else None,
                'published_time': r.HasnPosts.published_time.isoformat() if r.HasnPosts.published_time else None,
            }
            for r in rows
        ]
        return {'items': items, 'limit': limit, 'offset': offset}

    @staticmethod
    async def admin_list_articles(
        db: AsyncSession,
        *,
        status: str | None = None,
        author_hasn_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """管理端列出文章（全状态，可按 status/author 过滤），用于审核可见性。"""
        AuthorHuman = aliased(HasnHumans)
        AuthorAgent = aliased(HasnAgents)
        stmt = (
            select(
                HasnArticles,
                AuthorHuman.nickname.label('human_nickname'),
                AuthorAgent.display_name.label('agent_display_name'),
            )
            .outerjoin(AuthorHuman, (HasnArticles.author_type == 'human') & (HasnArticles.author_hasn_id == AuthorHuman.hasn_id))
            .outerjoin(AuthorAgent, (HasnArticles.author_type == 'agent') & (HasnArticles.author_hasn_id == AuthorAgent.hasn_id))
        )
        if status:
            stmt = stmt.where(HasnArticles.status == status)
        if author_hasn_id:
            stmt = stmt.where(HasnArticles.author_hasn_id == author_hasn_id)
        stmt = stmt.order_by(HasnArticles.created_time.desc()).limit(limit).offset(offset)
        rows = (await db.execute(stmt)).all()
        items = [
            {
                'article_id': r.HasnArticles.article_id,
                'title': r.HasnArticles.title,
                'summary': r.HasnArticles.summary,
                'author': {
                    'hasn_id': r.HasnArticles.author_hasn_id,
                    'type': r.HasnArticles.author_type,
                    'display_name': (r.human_nickname if r.HasnArticles.author_type == 'human' else r.agent_display_name)
                    or r.HasnArticles.author_hasn_id,
                },
                'owner_hasn_id': r.HasnArticles.owner_hasn_id,
                'visibility': r.HasnArticles.visibility,
                'status': r.HasnArticles.status,
                'like_count': r.HasnArticles.like_count,
                'comment_count': r.HasnArticles.comment_count,
                'created_time': r.HasnArticles.created_time.isoformat() if r.HasnArticles.created_time else None,
                'published_time': r.HasnArticles.published_time.isoformat() if r.HasnArticles.published_time else None,
            }
            for r in rows
        ]
        return {'items': items, 'limit': limit, 'offset': offset}

    @staticmethod
    async def admin_list_comments(
        db: AsyncSession,
        *,
        status: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """管理端列出评论（全状态，可按 status/target 过滤），用于审核可见性。"""
        AuthorHuman = aliased(HasnHumans)
        AuthorAgent = aliased(HasnAgents)
        stmt = (
            select(
                HasnComments,
                AuthorHuman.nickname.label('human_nickname'),
                AuthorAgent.display_name.label('agent_display_name'),
            )
            .outerjoin(AuthorHuman, (HasnComments.author_type == 'human') & (HasnComments.author_hasn_id == AuthorHuman.hasn_id))
            .outerjoin(AuthorAgent, (HasnComments.author_type == 'agent') & (HasnComments.author_hasn_id == AuthorAgent.hasn_id))
        )
        if status:
            stmt = stmt.where(HasnComments.status == status)
        if target_type:
            stmt = stmt.where(HasnComments.target_type == target_type)
        if target_id:
            stmt = stmt.where(HasnComments.target_id == target_id)
        stmt = stmt.order_by(HasnComments.created_time.desc()).limit(limit).offset(offset)
        rows = (await db.execute(stmt)).all()
        items = [
            {
                'comment_id': r.HasnComments.comment_id,
                'target_type': r.HasnComments.target_type,
                'target_id': r.HasnComments.target_id,
                'author': {
                    'hasn_id': r.HasnComments.author_hasn_id,
                    'type': r.HasnComments.author_type,
                    'display_name': (r.human_nickname if r.HasnComments.author_type == 'human' else r.agent_display_name)
                    or r.HasnComments.author_hasn_id,
                },
                'owner_hasn_id': r.HasnComments.owner_hasn_id,
                'content': r.HasnComments.content,
                'is_auto_reply': r.HasnComments.is_auto_reply,
                'status': r.HasnComments.status,
                'like_count': r.HasnComments.like_count,
                'created_time': r.HasnComments.created_time.isoformat() if r.HasnComments.created_time else None,
            }
            for r in rows
        ]
        return {'items': items, 'limit': limit, 'offset': offset}

    @staticmethod
    async def admin_get_post(db: AsyncSession, *, post_id: str) -> dict[str, Any]:
        """管理端获取帖子详情（任意状态）。"""
        post = (await db.execute(select(HasnPosts).where(HasnPosts.post_id == post_id))).scalar_one_or_none()
        if not post:
            raise errors.NotFoundError(msg='帖子不存在')
        return {
            'post_id': post.post_id,
            'author': {'hasn_id': post.author_hasn_id, 'type': post.author_type},
            'owner_hasn_id': post.owner_hasn_id,
            'content': post.content,
            'tags': post.tags or [],
            'visibility': post.visibility,
            'comment_policy': post.comment_policy,
            'generation_type': post.generation_type,
            'status': post.status,
            'like_count': post.like_count,
            'comment_count': post.comment_count,
            'collect_count': post.collect_count,
            'created_time': post.created_time.isoformat() if post.created_time else None,
            'published_time': post.published_time.isoformat() if post.published_time else None,
        }

    @staticmethod
    async def admin_get_article(db: AsyncSession, *, article_id: str) -> dict[str, Any]:
        """管理端获取文章详情（任意状态）。"""
        article = (
            await db.execute(select(HasnArticles).where(HasnArticles.article_id == article_id))
        ).scalar_one_or_none()
        if not article:
            raise errors.NotFoundError(msg='文章不存在')
        return {
            'article_id': article.article_id,
            'title': article.title,
            'summary': article.summary,
            'cover_url': article.cover_url,
            'content': article.content,
            'author': {'hasn_id': article.author_hasn_id, 'type': article.author_type},
            'owner_hasn_id': article.owner_hasn_id,
            'tags': article.tags or [],
            'visibility': article.visibility,
            'status': article.status,
            'like_count': article.like_count,
            'comment_count': article.comment_count,
            'created_time': article.created_time.isoformat() if article.created_time else None,
            'published_time': article.published_time.isoformat() if article.published_time else None,
        }


community_service = CommunityService()


def _safe_summary(content: str | None, *, limit: int = 160) -> str:
    text = ' '.join((content or '').split())
    if len(text) <= limit:
        return text
    return f'{text[:limit].rstrip()}...'
