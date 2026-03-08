from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_publish import hx_creator_publish_dao
from backend.app.creator.schema.hx_creator_publish import CreateHxCreatorPublishParam, UpdateHxCreatorPublishParam
from backend.app.creator.service.hx_creator_content_service import hx_creator_content_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.utils.timezone import timezone

router = APIRouter()


class AgentRecordPublishParam(BaseModel):
    """Agent 记录发布参数"""
    content_id: int = Field(description='内容ID')
    platform: str = Field(description='发布平台')
    publish_url: str | None = Field(None, description='发布链接')
    account_id: int | None = Field(None, description='平台账号ID')
    method: str | None = Field('manual', description='发布方式')


class AgentUpdatePublishParam(BaseModel):
    """Agent 更新发布数据参数"""
    status: str | None = Field(None, description='状态')
    publish_url: str | None = Field(None, description='发布链接')
    views: int | None = Field(None, description='阅读量')
    likes: int | None = Field(None, description='点赞数')
    comments: int | None = Field(None, description='评论数')
    shares: int | None = Field(None, description='分享数')
    favorites: int | None = Field(None, description='收藏数')
    metrics_json: dict | None = Field(None, description='更多数据指标')
    error_message: str | None = Field(None, description='错误信息')


@router.post(
    '',
    summary='记录发布',
    dependencies=[DependsJwtAuth],
)
async def agent_record_publish(
    request: Request,
    db: CurrentSessionTransaction,
    obj: AgentRecordPublishParam,
) -> ResponseModel:
    user_id = request.user.id

    # 校验内容归属
    content = await hx_creator_content_service.get(db=db, pk=obj.content_id)
    if content.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该内容')

    create_param = CreateHxCreatorPublishParam(
        content_id=obj.content_id,
        user_id=user_id,
        platform=obj.platform,
        publish_url=obj.publish_url,
        account_id=obj.account_id,
        method=obj.method,
        status='published',
        published_at=timezone.now(),
    )
    record = await hx_creator_publish_dao.create_return(db, create_param)
    return response_base.success(data={
        'id': record.id,
        'content_id': record.content_id,
        'platform': record.platform,
        'status': record.status,
    })


@router.get(
    '',
    summary='列出发布记录',
    dependencies=[DependsJwtAuth],
)
async def agent_list_publishes(
    request: Request,
    db: CurrentSession,
    content_id: Annotated[int | None, Query(description='内容ID筛选')] = None,
    platform: Annotated[str | None, Query(description='平台筛选')] = None,
    status: Annotated[str | None, Query(description='状态筛选')] = None,
    limit: Annotated[int, Query(description='返回条数', ge=1, le=100)] = 50,
) -> ResponseModel:
    user_id = request.user.id
    records = await hx_creator_publish_dao.get_by_user_id(
        db, user_id, content_id=content_id, platform=platform, status=status, limit=limit
    )
    return response_base.success(data=[
        {
            'id': r.id,
            'content_id': r.content_id,
            'platform': r.platform,
            'publish_url': r.publish_url,
            'status': r.status,
            'method': r.method,
            'published_at': r.published_at,
            'views': r.views,
            'likes': r.likes,
            'comments': r.comments,
            'shares': r.shares,
            'favorites': r.favorites,
            'metrics_updated_at': r.metrics_updated_at,
        }
        for r in records
    ])


@router.put(
    '/{pk}',
    summary='更新发布数据',
    dependencies=[DependsJwtAuth],
)
async def agent_update_publish(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='发布记录ID')],
    obj: AgentUpdatePublishParam,
) -> ResponseModel:
    user_id = request.user.id
    record = await hx_creator_publish_dao.get(db, pk)
    if not record:
        raise errors.NotFoundError(msg='发布记录不存在')
    if record.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该记录')

    update_param = UpdateHxCreatorPublishParam(
        content_id=record.content_id,
        user_id=user_id,
        platform=record.platform,
        publish_url=obj.publish_url or record.publish_url,
        account_id=record.account_id,
        status=obj.status or record.status,
        method=record.method,
        error_message=obj.error_message if obj.error_message is not None else record.error_message,
        published_at=record.published_at,
        views=obj.views if obj.views is not None else record.views,
        likes=obj.likes if obj.likes is not None else record.likes,
        comments=obj.comments if obj.comments is not None else record.comments,
        shares=obj.shares if obj.shares is not None else record.shares,
        favorites=obj.favorites if obj.favorites is not None else record.favorites,
        metrics_json=obj.metrics_json if obj.metrics_json is not None else record.metrics_json,
        metrics_updated_at=timezone.now(),
    )
    await hx_creator_publish_dao.update(db, pk, update_param)
    return response_base.success()
