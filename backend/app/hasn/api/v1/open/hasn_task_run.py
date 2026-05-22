"""任务执行记录 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_task_run import GetHasnTaskRunDetail
from backend.app.hasn.service.hasn_task_run_service import hasn_task_run_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取任务执行记录列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_task_run',
)
async def get_hasn_task_run(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnTaskRunDetail]]:
    page_data = await hasn_task_run_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取任务执行记录详情',
    name='open_get_hasn_task_run',
)
async def get_hasn_task_run(
    db: CurrentSession,
    pk: Annotated[int, Path(description='任务执行记录 ID')],
) -> ResponseSchemaModel[GetHasnTaskRunDetail]:
    hasn_task_run = await hasn_task_run_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_task_run)
