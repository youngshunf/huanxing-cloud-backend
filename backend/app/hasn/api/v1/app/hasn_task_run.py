"""任务执行记录 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.api.v1.app.hasn_task import _current_owner_id
from backend.app.hasn.service.hasn_task_service import hasn_task_service
from backend.app.hasn.schema.hasn_task_run import (
    CreateHasnTaskRunParam,
    GetHasnTaskRunDetail,
    UpdateHasnTaskRunParam,
)
from backend.app.hasn.service.hasn_task_run_service import hasn_task_run_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的任务执行记录列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_hasn_task_run',
)
async def get_my_hasn_task_run(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnTaskRunDetail]]:
    owner_id = await _current_owner_id(request, db)
    page_data = await hasn_task_run_service.get_list_by_owner(db=db, owner_id=owner_id)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建任务执行记录',
    dependencies=[DependsJwtAuth],
    name='app_create_my_hasn_task_run',
)
async def create_my_hasn_task_run(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnTaskRunParam,
) -> ResponseModel:
    result = await hasn_task_run_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取任务执行记录详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_hasn_task_run_detail',
)
async def get_my_hasn_task_run_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='任务执行记录 ID')],
) -> ResponseSchemaModel[GetHasnTaskRunDetail]:
    owner_id = await _current_owner_id(request, db)
    hasn_task_run = await hasn_task_run_service.get(db=db, pk=pk)
    task = await hasn_task_service.get(db=db, pk=hasn_task_run.task_id)
    if task.owner_id != owner_id:
        raise errors.ForbiddenError(msg='无权访问该任务执行记录')
    return response_base.success(data=hasn_task_run)


@router.put(
    '/{pk}',
    summary='更新任务执行记录',
    dependencies=[DependsJwtAuth],
    name='app_update_my_hasn_task_run',
)
async def update_my_hasn_task_run(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='任务执行记录 ID')],
    obj: UpdateHasnTaskRunParam,
) -> ResponseModel:
    owner_id = await _current_owner_id(request, db)
    hasn_task_run = await hasn_task_run_service.get(db=db, pk=pk)
    task = await hasn_task_service.get(db=db, pk=hasn_task_run.task_id)
    if task.owner_id != owner_id:
        raise errors.ForbiddenError(msg='无权修改该任务执行记录')
    count = await hasn_task_run_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除任务执行记录',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_hasn_task_run',
)
async def delete_my_hasn_task_run(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='任务执行记录 ID')],
) -> ResponseModel:
    owner_id = await _current_owner_id(request, db)
    hasn_task_run = await hasn_task_run_service.get(db=db, pk=pk)
    task = await hasn_task_service.get(db=db, pk=hasn_task_run.task_id)
    if task.owner_id != owner_id:
        raise errors.ForbiddenError(msg='无权删除该任务执行记录')
    from backend.app.hasn.schema.hasn_task_run import DeleteHasnTaskRunParam
    count = await hasn_task_run_service.delete(db=db, obj=DeleteHasnTaskRunParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
