"""任务定义 - 公开 API

认证方式: 无（公开接口，无需登录）
"""
from typing import Annotated

from fastapi import APIRouter, Path

from backend.app.hasn.schema.hasn_task import GetHasnTaskDetail
from backend.app.hasn.service.hasn_task_service import hasn_task_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='获取任务定义列表',
    dependencies=[DependsPagination],
    name='open_get_hasn_task',
)
async def get_hasn_task(
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnTaskDetail]]:
    page_data = await hasn_task_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/{pk}',
    summary='获取任务定义详情',
    name='open_get_hasn_task',
)
async def get_hasn_task(
    db: CurrentSession,
    pk: Annotated[int, Path(description='任务定义 ID')],
) -> ResponseSchemaModel[GetHasnTaskDetail]:
    hasn_task = await hasn_task_service.get(db=db, pk=pk)
    return response_base.success(data=hasn_task)
