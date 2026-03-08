from typing import Annotated

from fastapi import APIRouter, Query, Request

from backend.app.creator.crud.crud_hx_creator_publish import hx_creator_publish_dao
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='发布记录列表（分页 + 平台筛选）',
    dependencies=[DependsJwtAuth],
)
async def app_list_publishes(
    request: Request,
    db: CurrentSession,
    platform: Annotated[str | None, Query(description='平台筛选')] = None,
    page: Annotated[int, Query(description='页码', ge=1)] = 1,
    page_size: Annotated[int, Query(description='每页数量', ge=1, le=100)] = 20,
) -> ResponseModel:
    user_id = request.user.id
    limit = page_size * page
    publishes = await hx_creator_publish_dao.get_by_user_id(
        db, user_id, platform=platform, limit=limit
    )
    total = len(publishes)
    start = (page - 1) * page_size
    page_items = list(publishes)[start:start + page_size]
    return response_base.success(data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'items': [
            {
                'id': p.id,
                'content_id': p.content_id,
                'platform': p.platform,
                'publish_url': p.publish_url,
                'status': p.status,
                'views': p.views,
                'likes': p.likes,
                'comments': p.comments,
                'shares': p.shares,
                'favorites': p.favorites,
                'published_at': p.published_at,
                'created_time': p.created_time,
            }
            for p in page_items
        ],
    })
