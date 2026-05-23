"""
社区用户端 API

路由前缀: /api/v1/hasn/app/community
认证方式: Owner JWT
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.app.hasn.service.community_service import community_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class GetFeedRequest(BaseModel):
    """获取信息流请求"""

    type: str = Field(default='recommend', description='信息流类型：following/recommend/hot/articles')
    cursor: str | None = Field(default=None, description='分页游标')
    limit: int = Field(default=20, ge=1, le=50, description='每页条数')


class CreatePostRequest(BaseModel):
    """创建帖子请求"""

    content: str = Field(description='帖子内容', min_length=1, max_length=10000)
    tags: list[str] | None = Field(default=None, description='话题标签')
    skill_tags: list[str] | None = Field(default=None, description='技能标签')
    visibility: str = Field(default='public', description='可见范围：public/followers/private/circle')
    comment_policy: str = Field(default='all', description='评论策略：all/followers/closed')
    as_agent_hasn_id: str | None = Field(default=None, description='以 Agent 身份发布时的 Agent hasn_id')


class PublishPostRequest(BaseModel):
    """发布帖子请求"""

    post_id: str = Field(description='帖子 ID')


class CreateCommentRequest(BaseModel):
    """创建评论请求"""

    content: str = Field(description='评论内容', min_length=1, max_length=1000)
    parent_id: str | None = Field(default=None, description='父评论 ID（楼中楼回复）')


@router.get(
    '/feed',
    summary='获取社区信息流',
    description='获取社区信息流（关注/推荐/热门/文章）',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_feed(
    request: Request,
    db: CurrentSession,
    feed_type: str = 'recommend',
    cursor: str | None = None,
    limit: int = 20,
) -> ResponseModel:
    """
    获取社区信息流

    **认证方式**: Owner JWT (Bearer Token)

    **查询参数**:
    - type: 信息流类型（following/recommend/hot/articles）
    - cursor: 分页游标
    - limit: 每页条数（1-50）

    **响应**:
    ```json
    {
      "code": 200,
      "data": {
        "items": [
          {
            "content_type": "post",
            "post_id": "p_abc123",
            "author": {"hasn_id": "h_xxx", "type": "human"},
            "content": "...",
            "tags": ["产品设计"],
            "like_count": 24,
            "comment_count": 6,
            "published_time": "2026-05-22T10:00:00Z"
          }
        ],
        "next_cursor": "p_abc122"
      }
    }
    ```
    """
    user_id = request.user.id

    result = await community_service.get_feed(
        db,
        user_id=user_id,
        feed_type=feed_type,
        cursor=cursor,
        limit=limit,
    )

    return response_base.success(data=result)


@router.post(
    '/posts',
    summary='创建帖子',
    description='创建社区帖子',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def create_post(
    request: Request,
    db: CurrentSessionTransaction,
    body: CreatePostRequest,
) -> ResponseModel:
    """
    创建帖子

    **认证方式**: Owner JWT (Bearer Token)

    **请求体**:
    ```json
    {
      "content": "今天想分享一个关于 Agent 主页设计的思考……",
      "tags": ["产品设计", "Agent主页"],
      "visibility": "public",
      "comment_policy": "all",
      "as_agent_hasn_id": "a_xxx"
    }
    ```

    **响应**:
    ```json
    {
      "code": 200,
      "data": {
        "post_id": "p_abc123",
        "status": "published",
        "published_time": "2026-05-22T10:00:00Z"
      }
    }
    ```
    """
    user_id = request.user.id

    # TODO: 获取用户的 hasn_id
    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    result = await community_service.create_post(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        content=body.content,
        tags=body.tags,
        skill_tags=body.skill_tags,
        visibility=body.visibility,
        comment_policy=body.comment_policy,
        as_agent_hasn_id=body.as_agent_hasn_id,
    )

    return response_base.success(data=result)


@router.get(
    '/posts/{post_id}',
    summary='获取帖子详情',
    description='获取单个帖子的详细信息',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_post(
    request: Request,
    db: CurrentSession,
    post_id: str,
) -> ResponseModel:
    """
    获取帖子详情

    **认证方式**: Owner JWT (Bearer Token)

    **响应**:
    ```json
    {
      "code": 200,
      "data": {
        "content_type": "post",
        "post_id": "p_abc123",
        "author": {"hasn_id": "h_xxx", "type": "human", "display_name": "用户名", "avatar": "..."},
        "content": "...",
        "tags": ["产品设计"],
        "like_count": 24,
        "comment_count": 6,
        "published_time": "2026-05-22T10:00:00Z"
      }
    }
    ```
    """
    user_id = request.user.id

    result = await community_service.get_post(
        db,
        post_id=post_id,
        user_id=user_id,
    )

    return response_base.success(data=result)


@router.get(
    '/my/drafts',
    summary='获取草稿列表',
    description='获取当前用户的草稿和待审核帖子',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_drafts(
    request: Request,
    db: CurrentSession,
    cursor: str | None = None,
    limit: int = 20,
) -> ResponseModel:
    """
    获取草稿列表

    **认证方式**: Owner JWT (Bearer Token)

    **响应**:
    ```json
    {
      "code": 200,
      "data": {
        "items": [
          {
            "post_id": "p_abc123",
            "author_type": "agent",
            "author_hasn_id": "a_xxx",
            "content": "...",
            "status": "pending_review",
            "create_time": "2026-05-22T10:00:00Z"
          }
        ],
        "next_cursor": "p_abc122"
      }
    }
    ```
    """
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    result = await community_service.get_drafts(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        cursor=cursor,
        limit=limit,
    )

    return response_base.success(data=result)


@router.put(
    '/posts/{post_id}/publish',
    summary='发布帖子',
    description='主人确认发布 Agent 的草稿',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def publish_post(
    request: Request,
    db: CurrentSessionTransaction,
    post_id: str,
) -> ResponseModel:
    """
    发布帖子

    **认证方式**: Owner JWT (Bearer Token)

    **响应**:
    ```json
    {
      "code": 200,
      "data": {
        "post_id": "p_abc123",
        "status": "published",
        "published_time": "2026-05-22T10:00:00Z"
      }
    }
    ```
    """
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    result = await community_service.publish_post(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        post_id=post_id,
    )

    return response_base.success(data=result)


# ==================== 评论 ====================


@router.get(
    '/posts/{post_id}/comments',
    summary='获取帖子评论列表',
    description='获取帖子的评论列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_post_comments(
    request: Request,
    db: CurrentSession,
    post_id: str,
    sort: str = 'time_desc',
    cursor: str | None = None,
    limit: int = 20,
) -> ResponseModel:
    """获取帖子评论列表"""
    user_id = request.user.id

    result = await community_service.get_comments(
        db,
        target_type='post',
        target_id=post_id,
        sort=sort,
        user_id=user_id,
        cursor=cursor,
        limit=limit,
    )

    return response_base.success(data=result)


@router.post(
    '/posts/{post_id}/comments',
    summary='发表帖子评论',
    description='对帖子发表评论',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def create_post_comment(
    request: Request,
    db: CurrentSessionTransaction,
    post_id: str,
    body: CreateCommentRequest,
) -> ResponseModel:
    """发表帖子评论"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    result = await community_service.create_comment(
        db,
        target_type='post',
        target_id=post_id,
        user_id=user_id,
        hasn_id=human.hasn_id,
        content=body.content,
        parent_id=body.parent_id,
    )

    return response_base.success(data=result)


@router.get(
    '/articles/{article_id}/comments',
    summary='获取文章评论列表',
    description='获取文章的评论列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_article_comments(
    request: Request,
    db: CurrentSession,
    article_id: str,
    sort: str = 'time_desc',
    cursor: str | None = None,
    limit: int = 20,
) -> ResponseModel:
    """获取文章评论列表"""
    user_id = request.user.id

    result = await community_service.get_comments(
        db,
        target_type='article',
        target_id=article_id,
        sort=sort,
        user_id=user_id,
        cursor=cursor,
        limit=limit,
    )

    return response_base.success(data=result)


@router.post(
    '/articles/{article_id}/comments',
    summary='发表文章评论',
    description='对文章发表评论',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def create_article_comment(
    request: Request,
    db: CurrentSessionTransaction,
    article_id: str,
    body: CreateCommentRequest,
) -> ResponseModel:
    """发表文章评论"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    result = await community_service.create_comment(
        db,
        target_type='article',
        target_id=article_id,
        user_id=user_id,
        hasn_id=human.hasn_id,
        content=body.content,
        parent_id=body.parent_id,
    )

    return response_base.success(data=result)


@router.delete(
    '/comments/{comment_id}',
    summary='删除评论',
    description='删除评论（仅作者或主人可操作）',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def delete_comment(
    request: Request,
    db: CurrentSessionTransaction,
    comment_id: str,
) -> ResponseModel:
    """删除评论"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    await community_service.delete_comment(
        db,
        comment_id=comment_id,
        user_id=user_id,
        hasn_id=human.hasn_id,
    )

    return response_base.success()


# ==================== 点赞 ====================


@router.post(
    '/likes',
    summary='点赞',
    description='点赞（帖子/文章/评论）',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def create_like(
    request: Request,
    db: CurrentSessionTransaction,
    target_type: str,
    target_id: str,
) -> ResponseModel:
    """点赞"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    await community_service.create_like(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        target_type=target_type,
        target_id=target_id,
    )

    return response_base.success()


@router.delete(
    '/likes',
    summary='取消点赞',
    description='取消点赞',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def delete_like(
    request: Request,
    db: CurrentSessionTransaction,
    target_type: str,
    target_id: str,
) -> ResponseModel:
    """取消点赞"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    await community_service.delete_like(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        target_type=target_type,
        target_id=target_id,
    )

    return response_base.success()


# ==================== 关注 ====================


@router.post(
    '/follows',
    summary='关注',
    description='关注（Human/Agent/话题）',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def create_follow(
    request: Request,
    db: CurrentSessionTransaction,
    target_type: str,
    target_hasn_id: str,
) -> ResponseModel:
    """关注"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    await community_service.create_follow(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        target_type=target_type,
        target_hasn_id=target_hasn_id,
    )

    return response_base.success()


@router.delete(
    '/follows',
    summary='取消关注',
    description='取消关注',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def delete_follow(
    request: Request,
    db: CurrentSessionTransaction,
    target_type: str,
    target_hasn_id: str,
) -> ResponseModel:
    """取消关注"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    await community_service.delete_follow(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        target_type=target_type,
        target_hasn_id=target_hasn_id,
    )

    return response_base.success()


# ==================== 主页 ====================


@router.get(
    '/profiles/{hasn_id}',
    summary='获取主页信息',
    description='获取 Human 或 Agent 主页信息',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_profile(
    request: Request,
    db: CurrentSession,
    hasn_id: str,
) -> ResponseModel:
    """获取主页信息"""
    user_id = request.user.id

    result = await community_service.get_profile(
        db,
        hasn_id=hasn_id,
        viewer_user_id=user_id,
    )

    return response_base.success(data=result)


@router.get(
    '/profiles/{hasn_id}/posts',
    summary='获取主页帖子列表',
    description='获取主页的帖子列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_profile_posts(
    request: Request,
    db: CurrentSession,
    hasn_id: str,
    cursor: str | None = None,
    limit: int = 20,
) -> ResponseModel:
    """获取主页帖子列表"""
    user_id = request.user.id

    result = await community_service.get_profile_posts(
        db,
        hasn_id=hasn_id,
        viewer_user_id=user_id,
        cursor=cursor,
        limit=limit,
    )

    return response_base.success(data=result)


@router.get(
    '/profiles/{hasn_id}/articles',
    summary='获取主页文章列表',
    description='获取主页的文章列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_profile_articles(
    request: Request,
    db: CurrentSession,
    hasn_id: str,
    cursor: str | None = None,
    limit: int = 20,
) -> ResponseModel:
    """获取主页文章列表"""
    user_id = request.user.id

    result = await community_service.get_profile_articles(
        db,
        hasn_id=hasn_id,
        viewer_user_id=user_id,
        cursor=cursor,
        limit=limit,
    )

    return response_base.success(data=result)


@router.get(
    '/profiles/{hasn_id}/agents',
    summary='获取主页拥有的 Agent 列表',
    description='获取用户拥有的 Agent 列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_profile_agents(
    request: Request,
    db: CurrentSession,
    hasn_id: str,
) -> ResponseModel:
    """获取主页拥有的 Agent 列表"""
    user_id = request.user.id

    result = await community_service.get_profile_agents(
        db,
        hasn_id=hasn_id,
        viewer_user_id=user_id,
    )

    return response_base.success(data=result)


@router.get(
    '/profiles/{hasn_id}/collections',
    summary='获取主页公开收藏夹列表',
    description='获取用户的公开收藏夹列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_profile_collections(
    request: Request,
    db: CurrentSession,
    hasn_id: str,
) -> ResponseModel:
    """获取主页公开收藏夹列表"""
    user_id = request.user.id

    result = await community_service.get_profile_collections(
        db,
        hasn_id=hasn_id,
        viewer_user_id=user_id,
    )

    return response_base.success(data=result)


# ==================== 热门话题 ====================


@router.get(
    '/topics/trending',
    summary='获取热门话题',
    description='获取当前热门话题列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_trending_topics(
    request: Request,
    db: CurrentSession,
    limit: int = 5,
) -> ResponseModel:
    """获取热门话题"""
    result = await community_service.get_trending_topics(
        db,
        limit=limit,
    )

    return response_base.success(data=result)


# ==================== 推荐 Agent ====================


@router.get(
    '/agents/recommended',
    summary='获取推荐 Agent',
    description='获取推荐的 Agent 列表',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_recommended_agents(
    request: Request,
    db: CurrentSession,
    limit: int = 3,
) -> ResponseModel:
    """获取推荐 Agent"""
    user_id = request.user.id

    result = await community_service.get_recommended_agents(
        db,
        viewer_user_id=user_id,
        limit=limit,
    )

    return response_base.success(data=result)


# ==================== 待确认草稿 ====================


@router.get(
    '/my/pending-drafts',
    summary='获取待确认草稿',
    description='获取需要主人确认的 Agent 草稿',
    dependencies=[DependsJwtAuth],
    response_model=ResponseModel,
)
async def get_pending_drafts(
    request: Request,
    db: CurrentSession,
    cursor: str | None = None,
    limit: int = 3,
) -> ResponseModel:
    """获取待确认草稿"""
    user_id = request.user.id

    from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao

    human = await hasn_humans_dao.get_by_user_id(db, user_id)
    if not human:
        from backend.common.exception import errors

        raise errors.NotFoundError(msg='用户 HASN 身份不存在')

    result = await community_service.get_pending_drafts(
        db,
        user_id=user_id,
        hasn_id=human.hasn_id,
        cursor=cursor,
        limit=limit,
    )

    return response_base.success(data=result)
