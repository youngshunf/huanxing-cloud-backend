"""App Event 定义 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.app_platform.schema.app_events import (
    CreateAppEventsParam,
    GetAppEventsDetail,
    UpdateAppEventsParam,
)
from backend.app.app_platform.service.app_events_service import app_events_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的App Event 定义列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_app_eventss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetAppEventsDetail]]:
    page_data = await app_events_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App Event 定义',
    dependencies=[DependsJwtAuth],
)
async def create_my_app_events(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateAppEventsParam,
) -> ResponseModel:
    result = await app_events_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取App Event 定义详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_app_events(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='App Event 定义 ID')],
) -> ResponseSchemaModel[GetAppEventsDetail]:
    app_events = await app_events_service.get(db=db, pk=pk)
    if app_events.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该App Event 定义')
    return response_base.success(data=app_events)


@router.put(
    '/{pk}',
    summary='更新App Event 定义',
    dependencies=[DependsJwtAuth],
)
async def update_my_app_events(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App Event 定义 ID')],
    obj: UpdateAppEventsParam,
) -> ResponseModel:
    app_events = await app_events_service.get(db=db, pk=pk)
    if getattr(app_events, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该App Event 定义')
    count = await app_events_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除App Event 定义',
    dependencies=[DependsJwtAuth],
)
async def delete_my_app_events(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='App Event 定义 ID')],
) -> ResponseModel:
    user_id = request.user.id
    app_events = await app_events_service.get(db=db, pk=pk)
    if app_events.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该App Event 定义')
    from backend.app.app_platform.schema.app_events import DeleteAppEventsParam
    count = await app_events_service.delete(db=db, obj=DeleteAppEventsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
