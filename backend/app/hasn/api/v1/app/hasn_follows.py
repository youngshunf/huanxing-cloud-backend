"""社区关注 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_follows import (
    CreateHasnFollowsParam,
    GetHasnFollowsDetail,
    UpdateHasnFollowsParam,
)
from backend.app.hasn.service.hasn_follows_service import hasn_follows_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的社区关注列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_hasn_follows',
)
async def get_my_hasn_follows(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnFollowsDetail]]:
    page_data = await hasn_follows_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区关注',
    dependencies=[DependsJwtAuth],
    name='app_create_my_hasn_follows',
)
async def create_my_hasn_follows(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnFollowsParam,
) -> ResponseModel:
    result = await hasn_follows_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取社区关注详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_hasn_follows',
)
async def get_my_hasn_follows(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区关注 ID')],
) -> ResponseSchemaModel[GetHasnFollowsDetail]:
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    if hasn_follows.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该社区关注')
    return response_base.success(data=hasn_follows)


@router.put(
    '/{pk}',
    summary='更新社区关注',
    dependencies=[DependsJwtAuth],
    name='app_update_my_hasn_follows',
)
async def update_my_hasn_follows(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区关注 ID')],
    obj: UpdateHasnFollowsParam,
) -> ResponseModel:
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    if getattr(hasn_follows, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该社区关注')
    count = await hasn_follows_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除社区关注',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_hasn_follows',
)
async def delete_my_hasn_follows(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区关注 ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_follows = await hasn_follows_service.get(db=db, pk=pk)
    if hasn_follows.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该社区关注')
    from backend.app.hasn.schema.hasn_follows import DeleteHasnFollowsParam
    count = await hasn_follows_service.delete(db=db, obj=DeleteHasnFollowsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
