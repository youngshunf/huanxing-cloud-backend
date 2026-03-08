from typing import Annotated

from fastapi import APIRouter, Query, Request

from backend.app.creator.service.hx_creator_analytics_service import hx_creator_analytics_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '/overview',
    summary='数据总览',
    dependencies=[DependsJwtAuth],
)
async def agent_analytics_overview(
    request: Request,
    db: CurrentSession,
    days: Annotated[int, Query(description='统计天数', ge=1, le=365)] = 7,
) -> ResponseModel:
    user_id = request.user.id
    data = await hx_creator_analytics_service.overview(db=db, user_id=user_id, days=days)
    return response_base.success(data=data)


@router.get(
    '/top',
    summary='热门内容排行',
    dependencies=[DependsJwtAuth],
)
async def agent_analytics_top(
    request: Request,
    db: CurrentSession,
    metric: Annotated[str, Query(description='排序指标：views/likes/comments/shares/favorites')] = 'views',
    limit: Annotated[int, Query(description='返回条数', ge=1, le=50)] = 10,
) -> ResponseModel:
    user_id = request.user.id
    data = await hx_creator_analytics_service.top_contents(
        db=db, user_id=user_id, metric=metric, limit=limit
    )
    return response_base.success(data=data)
