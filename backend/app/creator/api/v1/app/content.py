from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field

from backend.app.creator.crud.crud_hx_creator_publish import hx_creator_publish_dao
from backend.app.creator.service.hx_creator_content_service import hx_creator_content_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class AppUpdateContentStatusParam(BaseModel):
    """更新内容状态参数"""
    status: str = Field(description='新状态')


@router.get(
    '',
    summary='内容列表（分页 + 状态筛选）',
    dependencies=[DependsJwtAuth],
)
async def app_list_contents(
    request: Request,
    db: CurrentSession,
    status: Annotated[str | None, Query(description='状态筛选')] = None,
    project_id: Annotated[int | None, Query(description='项目ID筛选')] = None,
    page: Annotated[int, Query(description='页码', ge=1)] = 1,
    page_size: Annotated[int, Query(description='每页数量', ge=1, le=100)] = 20,
) -> ResponseModel:
    user_id = request.user.id
    limit = page_size * page  # 简单实现：取 limit 后在内存切片
    contents = await hx_creator_content_service.get_by_user(
        db=db, user_id=user_id, status=status, project_id=project_id, limit=limit
    )
    # 内存分页
    total = len(contents)
    start = (page - 1) * page_size
    page_items = list(contents)[start:start + page_size]
    return response_base.success(data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'items': [
            {
                'id': c.id,
                'project_id': c.project_id,
                'title': c.title,
                'status': c.status,
                'target_platforms': c.target_platforms,
                'pipeline_mode': c.pipeline_mode,
                'created_time': c.created_time,
                'updated_time': c.updated_time,
            }
            for c in page_items
        ],
    })


@router.get(
    '/{pk}',
    summary='内容详情（含阶段产出+发布记录）',
    dependencies=[DependsJwtAuth],
)
async def app_get_content(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='内容ID')],
) -> ResponseModel:
    user_id = request.user.id
    content_detail = await hx_creator_content_service.get_with_stages(db=db, pk=pk, user_id=user_id)
    # 追加发布记录
    publishes = await hx_creator_publish_dao.get_by_content_id(db, pk)
    content_detail['publishes'] = [
        {
            'id': p.id,
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
        for p in publishes
    ]
    return response_base.success(data=content_detail)


@router.put(
    '/{pk}/status',
    summary='更新内容状态',
    dependencies=[DependsJwtAuth],
)
async def app_update_content_status(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='内容ID')],
    obj: AppUpdateContentStatusParam,
) -> ResponseModel:
    user_id = request.user.id
    await hx_creator_content_service.update_status(db=db, pk=pk, user_id=user_id, new_status=obj.status)
    return response_base.success()
