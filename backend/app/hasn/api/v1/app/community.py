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
from backend.database.db import CurrentSession

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
    db: CurrentSession,
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
    db: CurrentSession,
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
