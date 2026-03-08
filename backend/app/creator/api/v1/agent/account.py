from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_account import hx_creator_account_dao
from backend.app.creator.schema.hx_creator_account import CreateHxCreatorAccountParam, UpdateHxCreatorAccountParam
from backend.app.creator.service.hx_creator_project_service import hx_creator_project_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.utils.timezone import timezone

router = APIRouter()


class AgentAddAccountParam(BaseModel):
    """Agent 添加平台账号参数"""
    project_id: int | None = Field(None, description='项目ID（不传则使用活跃项目）')
    platform: str = Field(description='平台：xiaohongshu/douyin/wechat/weibo/bilibili')
    nickname: str | None = Field(None, description='平台昵称')
    platform_uid: str | None = Field(None, description='平台用户ID')
    avatar_url: str | None = Field(None, description='头像URL')
    bio: str | None = Field(None, description='简介')
    home_url: str | None = Field(None, description='主页链接')
    is_primary: bool | None = Field(None, description='是否主账号')
    notes: str | None = Field(None, description='备注')


class AgentUpdateMetricsParam(BaseModel):
    """Agent 更新账号指标参数"""
    followers: int | None = Field(None, description='粉丝数')
    following: int | None = Field(None, description='关注数')
    total_likes: int | None = Field(None, description='总点赞数')
    total_favorites: int | None = Field(None, description='总收藏数')
    total_comments: int | None = Field(None, description='总评论数')
    total_posts: int | None = Field(None, description='总发布数')
    metrics_json: dict | None = Field(None, description='更多指标JSON')


@router.post(
    '',
    summary='添加平台账号',
    dependencies=[DependsJwtAuth],
)
async def agent_add_account(
    request: Request,
    db: CurrentSessionTransaction,
    obj: AgentAddAccountParam,
) -> ResponseModel:
    user_id = request.user.id

    project_id = obj.project_id
    if not project_id:
        active_project = await hx_creator_project_service.get_active_project(db=db, user_id=user_id)
        if not active_project:
            raise errors.RequestError(msg='请先创建项目或指定 project_id')
        project_id = active_project.id

    project = await hx_creator_project_service.get(db=db, pk=project_id)
    if project.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该项目')

    create_param = CreateHxCreatorAccountParam(
        project_id=project_id,
        user_id=user_id,
        platform=obj.platform,
        nickname=obj.nickname,
        platform_uid=obj.platform_uid,
        avatar_url=obj.avatar_url,
        bio=obj.bio,
        home_url=obj.home_url,
        is_primary=obj.is_primary,
        notes=obj.notes,
    )
    account = await hx_creator_account_dao.create_return(db, create_param)
    return response_base.success(data={
        'id': account.id,
        'platform': account.platform,
        'nickname': account.nickname,
    })


@router.get(
    '',
    summary='列出平台账号',
    dependencies=[DependsJwtAuth],
)
async def agent_list_accounts(
    request: Request,
    db: CurrentSession,
    platform: Annotated[str | None, Query(description='按平台筛选')] = None,
) -> ResponseModel:
    user_id = request.user.id
    accounts = await hx_creator_account_dao.get_by_user_id(db, user_id, platform=platform)
    return response_base.success(data=[
        {
            'id': a.id,
            'project_id': a.project_id,
            'platform': a.platform,
            'nickname': a.nickname,
            'platform_uid': a.platform_uid,
            'home_url': a.home_url,
            'followers': a.followers,
            'total_likes': a.total_likes,
            'total_posts': a.total_posts,
            'is_primary': a.is_primary,
            'metrics_updated_at': a.metrics_updated_at,
        }
        for a in accounts
    ])


@router.put(
    '/{pk}/metrics',
    summary='更新账号指标',
    dependencies=[DependsJwtAuth],
)
async def agent_update_account_metrics(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='账号ID')],
    obj: AgentUpdateMetricsParam,
) -> ResponseModel:
    user_id = request.user.id
    account = await hx_creator_account_dao.get(db, pk)
    if not account:
        raise errors.NotFoundError(msg='账号不存在')
    if account.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该账号')

    update_param = UpdateHxCreatorAccountParam(
        project_id=account.project_id,
        user_id=user_id,
        platform=account.platform,
        nickname=account.nickname,
        platform_uid=account.platform_uid,
        avatar_url=account.avatar_url,
        bio=account.bio,
        home_url=account.home_url,
        followers=obj.followers if obj.followers is not None else account.followers,
        following=obj.following if obj.following is not None else account.following,
        total_likes=obj.total_likes if obj.total_likes is not None else account.total_likes,
        total_favorites=obj.total_favorites if obj.total_favorites is not None else account.total_favorites,
        total_comments=obj.total_comments if obj.total_comments is not None else account.total_comments,
        total_posts=obj.total_posts if obj.total_posts is not None else account.total_posts,
        metrics_json=obj.metrics_json if obj.metrics_json is not None else account.metrics_json,
        metrics_updated_at=timezone.now(),
        is_primary=account.is_primary,
    )
    await hx_creator_account_dao.update(db, pk, update_param)
    return response_base.success()
