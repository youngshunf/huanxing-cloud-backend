from typing import Annotated

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_profile import hx_creator_profile_dao
from backend.app.creator.schema.hx_creator_profile import CreateHxCreatorProfileParam, UpdateHxCreatorProfileParam
from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class AgentSetProfileParam(BaseModel):
    """Agent 设置画像参数"""
    project_id: int | None = Field(None, description='项目ID（不传则使用活跃项目）')
    niche: str = Field(description='赛道/领域')
    sub_niche: str | None = Field(None, description='细分赛道')
    persona: str | None = Field(None, description='人设定位')
    target_audience: str | None = Field(None, description='目标受众')
    tone: str | None = Field(None, description='内容调性')
    keywords: dict | None = Field(None, description='核心关键词')
    bio: str | None = Field(None, description='简介文案')
    content_pillars: dict | None = Field(None, description='内容支柱')
    posting_frequency: str | None = Field(None, description='发布频率')
    best_posting_time: str | None = Field(None, description='最佳发布时间')
    style_references: dict | None = Field(None, description='风格参考')
    taboo_topics: dict | None = Field(None, description='避免话题')


@router.post(
    '',
    summary='设置/更新画像',
    dependencies=[DependsJwtAuth],
)
async def agent_set_profile(
    request: Request,
    db: CurrentSessionTransaction,
    obj: AgentSetProfileParam,
) -> ResponseModel:
    user_id = request.user.id

    # 确定项目ID
    project_id = obj.project_id
    if not project_id:
        active_project = await hx_creator_project_service.get_active_project(db=db, user_id=user_id)
        if not active_project:
            raise errors.RequestError(msg='请先创建项目或指定 project_id')
        project_id = active_project.id

    # 检查项目归属
    project = await hx_creator_project_service.get(db=db, pk=project_id)
    if project.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该项目')

    # 查找现有画像
    existing = await hx_creator_profile_dao.get_by_project_id(db, project_id)

    if existing:
        # 更新现有画像
        update_param = UpdateHxCreatorProfileParam(
            project_id=project_id,
            user_id=user_id,
            niche=obj.niche,
            sub_niche=obj.sub_niche,
            persona=obj.persona,
            target_audience=obj.target_audience,
            tone=obj.tone,
            keywords=obj.keywords,
            bio=obj.bio,
            content_pillars=obj.content_pillars,
            posting_frequency=obj.posting_frequency,
            best_posting_time=obj.best_posting_time,
            style_references=obj.style_references,
            taboo_topics=obj.taboo_topics,
        )
        await hx_creator_profile_dao.update(db, existing.id, update_param)
        return response_base.success(data={'id': existing.id, 'action': 'updated'})
    else:
        # 创建新画像
        create_param = CreateHxCreatorProfileParam(
            project_id=project_id,
            user_id=user_id,
            niche=obj.niche,
            sub_niche=obj.sub_niche,
            persona=obj.persona,
            target_audience=obj.target_audience,
            tone=obj.tone,
            keywords=obj.keywords,
            bio=obj.bio,
            content_pillars=obj.content_pillars,
            posting_frequency=obj.posting_frequency,
            best_posting_time=obj.best_posting_time,
            style_references=obj.style_references,
            taboo_topics=obj.taboo_topics,
        )
        profile = await hx_creator_profile_dao.create_return(db, create_param)
        return response_base.success(data={'id': profile.id, 'action': 'created'})


@router.get(
    '/active',
    summary='获取当前活跃项目画像',
    dependencies=[DependsJwtAuth],
)
async def agent_get_active_profile(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    user_id = request.user.id
    active_project = await hx_creator_project_service.get_active_project(db=db, user_id=user_id)
    if not active_project:
        raise errors.NotFoundError(msg='没有活跃项目')

    profile = await hx_creator_profile_dao.get_by_project_id(db, active_project.id)
    if not profile:
        return response_base.success(data={
            'project_id': active_project.id,
            'project_name': active_project.name,
            'profile': None,
        })

    return response_base.success(data={
        'project_id': active_project.id,
        'project_name': active_project.name,
        'profile': {
            'id': profile.id,
            'niche': profile.niche,
            'sub_niche': profile.sub_niche,
            'persona': profile.persona,
            'target_audience': profile.target_audience,
            'tone': profile.tone,
            'keywords': profile.keywords,
            'bio': profile.bio,
            'content_pillars': profile.content_pillars,
            'posting_frequency': profile.posting_frequency,
            'best_posting_time': profile.best_posting_time,
            'style_references': profile.style_references,
            'taboo_topics': profile.taboo_topics,
            'pillar_weights': profile.pillar_weights,
        },
    })
