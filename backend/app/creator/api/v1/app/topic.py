from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.creator.crud.crud_hx_creator_topic import hx_creator_topic_dao
from backend.app.creator.service.hx_creator_topic_service import hx_creator_topic_service
from backend.common.exception import errors
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='选题列表（分页 + 状态筛选）',
    dependencies=[DependsJwtAuth],
)
async def app_list_topics(
    request: Request,
    db: CurrentSession,
    project_id: Annotated[int | None, Query(description='项目ID筛选')] = None,
    status: Annotated[int | None, Query(description='状态筛选：0-待处理 1-已采纳 2-已跳过')] = None,
    page: Annotated[int, Query(description='页码', ge=1)] = 1,
    page_size: Annotated[int, Query(description='每页数量', ge=1, le=100)] = 20,
) -> ResponseModel:
    user_id = request.user.id
    limit = page_size * page
    topics = await hx_creator_topic_service.get_by_user(
        db=db, user_id=user_id, project_id=project_id, status=status, limit=limit
    )
    total = len(topics)
    start = (page - 1) * page_size
    page_items = list(topics)[start:start + page_size]
    return response_base.success(data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'items': [
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
            for t in page_items
        ],
    })


@router.put(
    '/{pk}',
    summary='采纳(status=1) / 跳过(status=2) 选题',
    dependencies=[DependsJwtAuth],
)
async def app_update_topic(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='选题ID')],
    status: Annotated[int, Query(description='操作：1-采纳 2-跳过')],
) -> ResponseModel:
    user_id = request.user.id
    topic = await hx_creator_topic_dao.get(db, pk)
    if not topic:
        raise errors.NotFoundError(msg='选题不存在')
    if topic.user_id != user_id:
        raise errors.ForbiddenError(msg='无权操作该选题')
    if topic.status != 0:
        raise errors.RequestError(msg='该选题已被处理')

    if status == 1:
        # 采纳：自动创建内容
        result = await hx_creator_topic_service.adopt_topic(db=db, pk=pk, user_id=user_id)
        return response_base.success(data=result)
    elif status == 2:
        # 跳过
        await hx_creator_topic_dao.skip(db, pk)
        return response_base.success()
    else:
        raise errors.RequestError(msg='无效操作：status 必须为 1（采纳）或 2（跳过）')
