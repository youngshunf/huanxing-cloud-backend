from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_topic import hx_creator_topic_dao
from backend.app.creator.crud.crud_hx_creator_viral_pattern import hx_creator_viral_pattern_dao
from backend.app.creator.schema.hx_creator_topic import CreateHxCreatorTopicParam
from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.app.creator.service.hx_creator_topic_service import hx_creator_topic_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class AgentCreateTopicParam(BaseModel):
    """Agent 创建选题参数"""
    project_id: int | None = Field(None, description='项目ID（不传则使用活跃项目）')
    title: str = Field(description='选题标题')
    potential_score: float | None = Field(None, description='潜力评分')
    heat_index: float | None = Field(None, description='热度指数')
    reason: str | None = Field(None, description='推荐理由')
    keywords: dict | None = Field(None, description='关键词')
    creative_angles: dict | None = Field(None, description='创作角度')


@router.get(
    '',
    summary='获取选题推荐',
    dependencies=[DependsJwtAuth],
)
async def agent_list_topics(
    request: Request,
    db: CurrentSession,
    project_id: Annotated[int | None, Query(description='项目ID筛选')] = None,
    status: Annotated[int | None, Query(description='状态筛选：0-待处理 1-已采纳 2-已跳过')] = None,
    limit: Annotated[int, Query(description='返回条数', ge=1, le=50)] = 20,
) -> ResponseModel:
    user_id = request.user.id
    topics = await hx_creator_topic_service.get_by_user(
        db=db, user_id=user_id, project_id=project_id, status=status, limit=limit
    )
    return response_base.success(data=[
        {
            'id': t.id,
            'project_id': t.project_id,
            'title': t.title,
            'potential_score': t.potential_score,
            'heat_index': t.heat_index,
            'reason': t.reason,
            'keywords': t.keywords,
            'creative_angles': t.creative_angles,
            'status': t.status,
            'content_id': t.content_id,
            'created_time': t.created_time,
        }
        for t in topics
    ])


@router.post(
    '',
    summary='创建选题推荐',
    dependencies=[DependsJwtAuth],
)
async def agent_create_topic(
    request: Request,
    db: CurrentSessionTransaction,
    obj: AgentCreateTopicParam,
) -> ResponseModel:
    user_id = request.user.id

    project_id = obj.project_id
    if not project_id:
        active_project = await hx_creator_project_service.get_active_project(db=db, user_id=user_id)
        if not active_project:
            raise errors.RequestError(msg='请先创建项目或指定 project_id')
        project_id = active_project.id

    create_param = CreateHxCreatorTopicParam(
        project_id=project_id,
        user_id=user_id,
        title=obj.title,
        potential_score=obj.potential_score,
        heat_index=obj.heat_index,
        reason=obj.reason,
        keywords=obj.keywords,
        creative_angles=obj.creative_angles,
        status=0,
    )
    topic = await hx_creator_topic_service.create_return(db=db, obj=create_param)
    return response_base.success(data={
        'id': topic.id,
        'title': topic.title,
    })


@router.put(
    '/{pk}/adopt',
    summary='采纳选题（自动创建内容）',
    dependencies=[DependsJwtAuth],
)
async def agent_adopt_topic(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='选题ID')],
) -> ResponseModel:
    user_id = request.user.id
    result = await hx_creator_topic_service.adopt_topic(db=db, pk=pk, user_id=user_id)
    return response_base.success(data=result)


@router.put(
    '/{pk}/skip',
    summary='跳过选题',
    dependencies=[DependsJwtAuth],
)
async def agent_skip_topic(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='选题ID')],
) -> ResponseModel:
    user_id = request.user.id
    topic = await hx_creator_topic_dao.get(db, pk)
    if not topic:
        raise errors.NotFoundError(msg='选题不存在')
    if topic.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该选题')
    if topic.status != 0:
        raise errors.RequestError(msg='该选题已被处理')
    await hx_creator_topic_dao.skip(db, pk)
    return response_base.success()


@router.get(
    '/patterns',
    summary='搜索爆款模式',
    dependencies=[DependsJwtAuth],
)
async def agent_search_patterns(
    request: Request,
    db: CurrentSession,
    category: Annotated[str | None, Query(description='分类筛选')] = None,
    platform: Annotated[str | None, Query(description='平台筛选')] = None,
    keyword: Annotated[str | None, Query(description='关键词搜索')] = None,
    limit: Annotated[int, Query(description='返回条数', ge=1, le=50)] = 20,
) -> ResponseModel:
    user_id = request.user.id
    patterns = await hx_creator_viral_pattern_dao.search(
        db, user_id=user_id, category=category, platform=platform, keyword=keyword, limit=limit
    )
    return response_base.success(data=[
        {
            'id': p.id,
            'category': p.category,
            'name': p.name,
            'platform': p.platform,
            'description': p.description,
            'template': p.template,
            'examples': p.examples,
            'source': p.source,
            'usage_count': p.usage_count,
            'success_rate': p.success_rate,
            'tags': p.tags,
        }
        for p in patterns
    ])
