from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Query, Request
from sqlalchemy import func, select

from backend.app.creator.model import HxCreatorContent, HxCreatorPublish
from backend.app.creator.service.hx_creator_analytics_service import hx_creator_analytics_service
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession
from backend.utils.timezone import timezone

router = APIRouter()


@router.get(
    '/overview',
    summary='数据总览',
    dependencies=[DependsJwtAuth],
)
async def app_analytics_overview(
    request: Request,
    db: CurrentSession,
    days: Annotated[int, Query(description='统计天数', ge=1, le=365)] = 7,
) -> ResponseModel:
    user_id = request.user.id
    data = await hx_creator_analytics_service.overview(db=db, user_id=user_id, days=days)
    return response_base.success(data=data)


@router.get(
    '/trend',
    summary='趋势数据（按日聚合，给折线图用）',
    dependencies=[DependsJwtAuth],
)
async def app_analytics_trend(
    request: Request,
    db: CurrentSession,
    days: Annotated[int, Query(description='统计天数', ge=7, le=90)] = 7,
) -> ResponseModel:
    user_id = request.user.id
    since = timezone.now() - timedelta(days=days)

    # 按日期聚合发布数据（views/likes/comments）
    stmt = (
        select(
            func.date(HxCreatorPublish.published_at).label('date'),
            func.coalesce(func.sum(HxCreatorPublish.views), 0).label('views'),
            func.coalesce(func.sum(HxCreatorPublish.likes), 0).label('likes'),
            func.coalesce(func.sum(HxCreatorPublish.comments), 0).label('comments'),
            func.count(HxCreatorPublish.id).label('publishes'),
        )
        .where(
            HxCreatorPublish.user_id == user_id,
            HxCreatorPublish.published_at >= since,
        )
        .group_by(func.date(HxCreatorPublish.published_at))
        .order_by(func.date(HxCreatorPublish.published_at))
    )
    result = await db.execute(stmt)
    rows = result.all()

    # 补全没有数据的日期
    date_map: dict[str, dict] = {}
    for row in rows:
        date_str = str(row[0])
        date_map[date_str] = {
            'date': date_str,
            'views': int(row[1]),
            'likes': int(row[2]),
            'comments': int(row[3]),
            'publishes': int(row[4]),
        }

    trend = []
    for i in range(days):
        day = timezone.now() - timedelta(days=days - 1 - i)
        date_str = day.strftime('%Y-%m-%d')
        trend.append(date_map.get(date_str, {
            'date': date_str,
            'views': 0,
            'likes': 0,
            'comments': 0,
            'publishes': 0,
        }))

    return response_base.success(data={'days': days, 'trend': trend})


@router.get(
    '/top',
    summary='热门内容排行（Top 10）',
    dependencies=[DependsJwtAuth],
)
async def app_analytics_top(
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
