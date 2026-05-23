"""任务定义 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao
from backend.app.hasn.schema.hasn_task import (
    CreateHasnTaskParam,
    GetHasnTaskDetail,
    UpdateHasnTaskParam,
)
from backend.app.hasn.service.hasn_task_service import hasn_task_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


async def _current_owner_id(request: Request, db: CurrentSession) -> str:
    owner_id = getattr(request.user, 'hasn_id', None)
    if owner_id:
        return owner_id
    hasn_human = await hasn_humans_dao.get_by_user_id(db, user_id=request.user.id)
    if not hasn_human:
        raise errors.ForbiddenError(msg='当前用户未注册 HASN 身份')
    return hasn_human.hasn_id


@router.get(
    '',
    summary='获取我的任务定义列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_hasn_task',
)
async def get_my_hasn_task(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnTaskDetail]]:
    owner_id = await _current_owner_id(request, db)
    page_data = await hasn_task_service.get_list_by_owner(db=db, owner_id=owner_id)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建任务定义',
    dependencies=[DependsJwtAuth],
    name='app_create_my_hasn_task',
)
async def create_my_hasn_task(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnTaskParam,
) -> ResponseModel:
    owner_id = await _current_owner_id(request, db)
    obj.owner_id = owner_id
    result = await hasn_task_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取任务定义详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_hasn_task_detail',
)
async def get_my_hasn_task_detail(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='任务定义 ID')],
) -> ResponseSchemaModel[GetHasnTaskDetail]:
    owner_id = await _current_owner_id(request, db)
    hasn_task = await hasn_task_service.get(db=db, pk=pk)
    if hasn_task.owner_id != owner_id:
        raise errors.ForbiddenError(msg='无权访问该任务定义')
    return response_base.success(data=hasn_task)


@router.put(
    '/{pk}',
    summary='更新任务定义',
    dependencies=[DependsJwtAuth],
    name='app_update_my_hasn_task',
)
async def update_my_hasn_task(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='任务定义 ID')],
    obj: UpdateHasnTaskParam,
) -> ResponseModel:
    owner_id = await _current_owner_id(request, db)
    hasn_task = await hasn_task_service.get(db=db, pk=pk)
    if hasn_task.owner_id != owner_id:
        raise errors.ForbiddenError(msg='无权修改该任务定义')
    obj.owner_id = owner_id
    count = await hasn_task_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除任务定义',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_hasn_task',
)
async def delete_my_hasn_task(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='任务定义 ID')],
) -> ResponseModel:
    owner_id = await _current_owner_id(request, db)
    hasn_task = await hasn_task_service.get(db=db, pk=pk)
    if hasn_task.owner_id != owner_id:
        raise errors.ForbiddenError(msg='无权删除该任务定义')
    from backend.app.hasn.schema.hasn_task import DeleteHasnTaskParam
    count = await hasn_task_service.delete(db=db, obj=DeleteHasnTaskParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
