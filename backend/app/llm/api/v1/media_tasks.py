"""媒体任务管理 API（管理后台）"""

from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.llm.crud.crud_media_task import media_task_dao
from backend.app.llm.schema.media_task import MediaTaskResult
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession

router = APIRouter()


@router.get('', summary='获取媒体任务列表', dependencies=[DependsJwtAuth, DependsPagination])
async def get_media_task_list(
    db: CurrentSession,
    user_id: Annotated[int | None, Query(description='用户 ID')] = None,
    media_type: Annotated[str | None, Query(description='媒体类型')] = None,
    status: Annotated[str | None, Query(description='任务状态')] = None,
    model_name: Annotated[str | None, Query(description='模型名称')] = None,
) -> ResponseModel:
    stmt = await media_task_dao.get_list(
        user_id=user_id,
        media_type=media_type,
        status=status,
    )
    page_data = await paging_data(db, stmt, MediaTaskResult)
    return response_base.success(data=page_data)


@router.get('/{pk}', summary='获取媒体任务详情', dependencies=[DependsJwtAuth])
async def get_media_task(db: CurrentSession, pk: int) -> ResponseModel:
    task = await media_task_dao.get(db, pk)
    if not task:
        return response_base.fail(msg='任务不存在')
    return response_base.success(data=MediaTaskResult.model_validate(task))


@router.delete('/{pk}', summary='删除媒体任务', dependencies=[DependsJwtAuth])
async def delete_media_task(db: CurrentSession, pk: int) -> ResponseModel:
    task = await media_task_dao.get(db, pk)
    if not task:
        return response_base.fail(msg='任务不存在')
    await media_task_dao.delete(db, pk)
    return response_base.success()
