"""社区帖子 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_posts import (
    CreateHasnPostsParam,
    GetHasnPostsDetail,
    UpdateHasnPostsParam,
)
from backend.app.hasn.service.hasn_posts_service import hasn_posts_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的社区帖子列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_hasn_posts',
)
async def get_my_hasn_posts(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnPostsDetail]]:
    page_data = await hasn_posts_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区帖子',
    dependencies=[DependsJwtAuth],
    name='app_create_my_hasn_posts',
)
async def create_my_hasn_posts(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnPostsParam,
) -> ResponseModel:
    result = await hasn_posts_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取社区帖子详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_hasn_posts',
)
async def get_my_hasn_posts(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区帖子 ID')],
) -> ResponseSchemaModel[GetHasnPostsDetail]:
    hasn_posts = await hasn_posts_service.get(db=db, pk=pk)
    if hasn_posts.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该社区帖子')
    return response_base.success(data=hasn_posts)


@router.put(
    '/{pk}',
    summary='更新社区帖子',
    dependencies=[DependsJwtAuth],
    name='app_update_my_hasn_posts',
)
async def update_my_hasn_posts(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区帖子 ID')],
    obj: UpdateHasnPostsParam,
) -> ResponseModel:
    hasn_posts = await hasn_posts_service.get(db=db, pk=pk)
    if getattr(hasn_posts, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该社区帖子')
    count = await hasn_posts_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除社区帖子',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_hasn_posts',
)
async def delete_my_hasn_posts(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区帖子 ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_posts = await hasn_posts_service.get(db=db, pk=pk)
    if hasn_posts.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该社区帖子')
    from backend.app.hasn.schema.hasn_posts import DeleteHasnPostsParam
    count = await hasn_posts_service.delete(db=db, obj=DeleteHasnPostsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
