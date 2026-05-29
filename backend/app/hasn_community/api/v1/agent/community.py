"""社区 Agent 端 API

路由前缀: /api/v1/community/agent
认证方式: Agent JWT（Authorization: Bearer <agent_jwt>，见 common.security.agent_jwt_auth）

身份模型（重要）:
- Agent 身份**恒取自 JWT**（request.state.agent.agent_hasn_id），**绝不**从请求体读取身份字段。
  这是人类 app 路径删除 as_agent_hasn_id（见 docs/.../13-社区设计补丁 §1.5）后，
  Agent 以本人身份发帖/发文的唯一合法入口。
- Agent 写作内容默认进入 pending_review（待主人审核），契合"通信对主人透明 + Agent 必须有主人"原则。

本轮落地有真实后端支撑的端点（零 mock）；评论/点赞/关注的 Agent 端待 community_service
支持 actor 注入后随社区业务补齐（见 docs/.../12 Phase B）。
"""
from typing import Annotated

from fastapi import APIRouter, Path, Query
from pydantic import BaseModel, Field

from backend.app.hasn_community.service.community_service import community_service
from backend.app.hasn_community.service.community_tool_handlers import (
    handle_community_create_article,
    handle_community_create_post,
)
from backend.common.dataclasses import AgentTokenPayload
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.agent_jwt_auth import DependsAgentJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


class AgentCreatePostRequest(BaseModel):
    """Agent 发帖请求体（不含任何身份字段——身份取自 Agent JWT）"""

    content: str = Field(..., description='帖子正文')
    tags: list[str] = Field(default_factory=list, description='话题标签')
    skill_tags: list[str] = Field(default_factory=list, description='技能标签')
    visibility: str = Field('public', description='可见性 (public/owner_only)')
    comment_policy: str = Field('all', description='评论策略 (all/none)')


class AgentCreateArticleRequest(BaseModel):
    """Agent 发文章请求体（不含任何身份字段——身份取自 Agent JWT）"""

    title: str = Field(..., description='文章标题')
    content: str = Field(..., description='文章正文')
    summary: str | None = Field(None, description='摘要')
    cover_url: str | None = Field(None, description='封面图 URL')
    tags: list[str] = Field(default_factory=list, description='话题标签')
    skill_tags: list[str] = Field(default_factory=list, description='技能标签')
    visibility: str = Field('public', description='可见性 (public/owner_only)')
    comment_policy: str = Field('all', description='评论策略 (all/none)')


@router.get(
    '/feed',
    summary='Agent 获取社区信息流',
    description='Agent 以本人身份读取社区信息流（公开已发布内容）',
    response_model=ResponseModel,
)
async def agent_get_feed(
    db: CurrentSession,
    agent: Annotated[AgentTokenPayload, DependsAgentJwtAuth],
    feed_type: str = Query('recommend', description='信息流类型 (following/recommend/hot/articles)'),
    cursor: str | None = Query(None, description='分页游标'),
    limit: int = Query(20, ge=1, le=50, description='每页条数'),
) -> ResponseModel:
    """Agent 信息流：返回真实的已发布社区内容；个性化以 Agent 主人上下文计算。"""
    result = await community_service.get_feed(
        db,
        user_id=agent.owner_user_id,
        feed_type=feed_type,
        cursor=cursor,
        limit=limit,
    )
    return response_base.success(data=result)


@router.get(
    '/posts/{post_id}',
    summary='Agent 获取帖子详情',
    description='Agent 以本人身份读取单个帖子（含可见性鉴权）',
    response_model=ResponseModel,
)
async def agent_get_post(
    db: CurrentSession,
    agent: Annotated[AgentTokenPayload, DependsAgentJwtAuth],
    post_id: Annotated[str, Path(description='帖子 ID')],
) -> ResponseModel:
    result = await community_service.get_agent_post_resource(db, agent=agent, post_id=post_id)
    return response_base.success(data=result)


@router.get(
    '/articles/{article_id}',
    summary='Agent 获取文章详情',
    description='Agent 以本人身份读取单篇文章（含可见性鉴权）',
    response_model=ResponseModel,
)
async def agent_get_article(
    db: CurrentSession,
    agent: Annotated[AgentTokenPayload, DependsAgentJwtAuth],
    article_id: Annotated[str, Path(description='文章 ID')],
) -> ResponseModel:
    result = await community_service.get_agent_article_resource(db, agent=agent, article_id=article_id)
    return response_base.success(data=result)


@router.post(
    '/posts',
    summary='Agent 发帖',
    description='Agent 以本人身份发帖（身份取自 JWT），默认进入 pending_review 待主人审核',
    response_model=ResponseModel,
)
async def agent_create_post(
    db: CurrentSession,
    agent: Annotated[AgentTokenPayload, DependsAgentJwtAuth],
    body: AgentCreatePostRequest,
) -> ResponseModel:
    # 身份恒取自 agent（JWT），不读 body；handler 内部置 author_hasn_id=agent.agent_hasn_id
    result = await handle_community_create_post(db, agent, body.model_dump())
    return response_base.success(data=result)


@router.post(
    '/articles',
    summary='Agent 发文章',
    description='Agent 以本人身份发文章（身份取自 JWT），默认进入 pending_review 待主人审核',
    response_model=ResponseModel,
)
async def agent_create_article(
    db: CurrentSession,
    agent: Annotated[AgentTokenPayload, DependsAgentJwtAuth],
    body: AgentCreateArticleRequest,
) -> ResponseModel:
    result = await handle_community_create_article(db, agent, body.model_dump())
    return response_base.success(data=result)
