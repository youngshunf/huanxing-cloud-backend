from typing import Annotated

from fastapi import APIRouter, Path, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_account import hx_creator_account_dao
from backend.app.creator.crud.crud_hx_creator_profile import hx_creator_profile_dao
from backend.app.creator.schema.hx_creator_project import UpdateHxCreatorProjectParam
from backend.app.creator.schema.hx_creator_profile import UpdateHxCreatorProfileParam
from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.app.creator.service.hx_creator_profile_service import hx_creator_profile_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class AppUpdateProjectParam(BaseModel):
    """用户更新项目参数"""
    name: str | None = Field(None, description='项目名称')
    description: str | None = Field(None, description='项目描述')
    platform: str | None = Field(None, description='主平台')
    platforms: dict | None = Field(None, description='多平台JSON数组')
    avatar_url: str | None = Field(None, description='项目头像URL')


class AppUpdateProfileParam(BaseModel):
    """用户更新画像参数"""
    niche: str | None = Field(None, description='赛道/领域')
    sub_niche: str | None = Field(None, description='细分赛道')
    persona: str | None = Field(None, description='人设')
    target_audience: str | None = Field(None, description='目标受众描述')
    tone: str | None = Field(None, description='内容调性')
    keywords: dict | None = Field(None, description='核心关键词')
    bio: str | None = Field(None, description='简介文案')
    content_pillars: dict | None = Field(None, description='内容支柱')
    posting_frequency: str | None = Field(None, description='发布频率')
    best_posting_time: str | None = Field(None, description='最佳发布时间')


@router.get(
    '',
    summary='我的项目列表',
    dependencies=[DependsJwtAuth],
)
async def app_list_projects(
    request: Request,
    db: CurrentSession,
) -> ResponseModel:
    user_id = request.user.id
    projects = await hx_creator_project_service.get_by_user(db=db, user_id=user_id)
    return response_base.success(data=[
        {
            'id': p.id,
            'name': p.name,
            'platform': p.platform,
            'platforms': p.platforms,
            'description': p.description,
            'is_active': p.is_active,
            'avatar_url': p.avatar_url,
            'created_time': p.created_time,
        }
        for p in projects
    ])


@router.get(
    '/{pk}',
    summary='项目详情（含画像+账号列表）',
    dependencies=[DependsJwtAuth],
)
async def app_get_project(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='项目ID')],
) -> ResponseModel:
    user_id = request.user.id
    project = await hx_creator_project_service.get(db=db, pk=pk)
    if project.user_id != user_id:
        raise errors.ForbiddenError(msg='无权访问该项目')

    profile = await hx_creator_profile_dao.get_by_project_id(db, pk)
    accounts = await hx_creator_account_dao.get_by_project_id(db, pk)

    return response_base.success(data={
        'id': project.id,
        'name': project.name,
        'platform': project.platform,
        'platforms': project.platforms,
        'description': project.description,
        'is_active': project.is_active,
        'avatar_url': project.avatar_url,
        'created_time': project.created_time,
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
        } if profile else None,
        'accounts': [
            {
                'id': a.id,
                'platform': a.platform,
                'nickname': a.nickname,
                'account_id': a.account_id,
                'followers': a.followers,
                'avg_views': a.avg_views,
                'avg_likes': a.avg_likes,
                'status': a.status,
            }
            for a in accounts
        ],
    })


@router.put(
    '/{pk}',
    summary='更新项目基本信息',
    dependencies=[DependsJwtAuth],
)
async def app_update_project(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='项目ID')],
    obj: AppUpdateProjectParam,
) -> ResponseModel:
    user_id = request.user.id
    project = await hx_creator_project_service.get(db=db, pk=pk)
    if project.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该项目')
    update_data = obj.model_dump(exclude_unset=True)
    if update_data:
        update_param = UpdateHxCreatorProjectParam(
            user_id=user_id,
            name=update_data.get('name', project.name),
            platform=update_data.get('platform', project.platform),
            description=update_data.get('description', project.description),
            platforms=update_data.get('platforms', project.platforms),
            avatar_url=update_data.get('avatar_url', project.avatar_url),
            is_active=project.is_active,
        )
        await hx_creator_project_service.update(db=db, pk=pk, obj=update_param)
    return response_base.success()


@router.put(
    '/{pk}/profile',
    summary='更新项目画像',
    dependencies=[DependsJwtAuth],
)
async def app_update_project_profile(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='项目ID')],
    obj: AppUpdateProfileParam,
) -> ResponseModel:
    user_id = request.user.id
    project = await hx_creator_project_service.get(db=db, pk=pk)
    if project.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该项目')

    profile = await hx_creator_profile_dao.get_by_project_id(db, pk)
    if not profile:
        raise errors.NotFoundError(msg='画像不存在')

    update_data = obj.model_dump(exclude_unset=True)
    if update_data:
        update_param = UpdateHxCreatorProfileParam(
            project_id=profile.project_id,
            user_id=user_id,
            niche=update_data.get('niche', profile.niche),
            sub_niche=update_data.get('sub_niche', profile.sub_niche),
            persona=update_data.get('persona', profile.persona),
            target_audience=update_data.get('target_audience', profile.target_audience),
            tone=update_data.get('tone', profile.tone),
            keywords=update_data.get('keywords', profile.keywords),
            bio=update_data.get('bio', profile.bio),
            content_pillars=update_data.get('content_pillars', profile.content_pillars),
            posting_frequency=update_data.get('posting_frequency', profile.posting_frequency),
            best_posting_time=update_data.get('best_posting_time', profile.best_posting_time),
            style_references=profile.style_references,
            taboo_topics=profile.taboo_topics,
            pillar_weights=profile.pillar_weights,
            pillar_weights_updated_at=profile.pillar_weights_updated_at,
        )
        await hx_creator_profile_service.update(db=db, pk=profile.id, obj=update_param)
    return response_base.success()
