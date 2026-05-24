"""任务系统 Task API

用于任务系统的任务管理，包括：
- 任务 CRUD
- 任务启用/禁用
"""
from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from backend.app.hasn.schema.hasn_task import CreateHasnTaskParam, UpdateHasnTaskParam
from backend.app.hasn.service.hasn_task_service import hasn_task_service
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.pagination import DependsPagination, PageData
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '/tasks',
    summary='查询任务列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='hasn_task_list',
)
async def task_list(
    request: Request,
    db: CurrentSession,
    enabled: Annotated[bool | None, Query(description="是否启用")] = None,
    state: Annotated[str | None, Query(description="任务状态")] = None,
) -> ResponseModel:
    """查询任务列表"""
    # TODO: 实现过滤逻辑
    page_data = await hasn_task_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '/tasks',
    summary='创建任务',
    dependencies=[DependsJwtAuth],
    name='hasn_task_create',
)
async def task_create(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnTaskParam,
) -> ResponseModel:
    """创建任务"""
    task = await hasn_task_service.create_with_schedule(db=db, obj=obj)
    return response_base.success(data={'task_id': task.id})


@router.get(
    '/tasks/{task_id}',
    summary='查询任务详情',
    dependencies=[DependsJwtAuth],
    name='hasn_task_detail',
)
async def task_detail(
    request: Request,
    db: CurrentSession,
    task_id: Annotated[int, Path(description="任务 ID")],
) -> ResponseModel:
    """查询任务详情"""
    task = await hasn_task_service.get(db=db, pk=task_id)
    return response_base.success(data=task)


@router.put(
    '/tasks/{task_id}',
    summary='更新任务',
    dependencies=[DependsJwtAuth],
    name='hasn_task_update',
)
async def task_update(
    request: Request,
    db: CurrentSessionTransaction,
    task_id: Annotated[int, Path(description="任务 ID")],
    obj: UpdateHasnTaskParam,
) -> ResponseModel:
    """更新任务"""
    count = await hasn_task_service.update(db=db, pk=task_id, obj=obj)
    return response_base.success(data={'updated': count})


@router.delete(
    '/tasks/{task_id}',
    summary='删除任务',
    dependencies=[DependsJwtAuth],
    name='hasn_task_delete',
)
async def task_delete(
    request: Request,
    db: CurrentSessionTransaction,
    task_id: Annotated[int, Path(description="任务 ID")],
) -> ResponseModel:
    """删除任务"""
    from backend.app.hasn.schema.hasn_task import DeleteHasnTaskParam
    count = await hasn_task_service.delete(db=db, obj=DeleteHasnTaskParam(pks=[task_id]))
    return response_base.success(data={'deleted': count})


@router.post(
    '/tasks/{task_id}/enable',
    summary='启用任务',
    dependencies=[DependsJwtAuth],
    name='hasn_task_enable',
)
async def task_enable(
    request: Request,
    db: CurrentSessionTransaction,
    task_id: Annotated[int, Path(description="任务 ID")],
) -> ResponseModel:
    """启用任务"""
    task = await hasn_task_service.enable_task(db=db, task_id=task_id)
    return response_base.success(data={'task_id': task.id, 'enabled': task.enabled})


@router.post(
    '/tasks/{task_id}/disable',
    summary='禁用任务',
    dependencies=[DependsJwtAuth],
    name='hasn_task_disable',
)
async def task_disable(
    request: Request,
    db: CurrentSessionTransaction,
    task_id: Annotated[int, Path(description="任务 ID")],
) -> ResponseModel:
    """禁用任务"""
    task = await hasn_task_service.disable_task(db=db, task_id=task_id)
    return response_base.success(data={'task_id': task.id, 'enabled': task.enabled})
