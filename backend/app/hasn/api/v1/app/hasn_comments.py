"""社区评论 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_comments import (
    CreateHasnCommentsParam,
    GetHasnCommentsDetail,
    UpdateHasnCommentsParam,
)
from backend.app.hasn.service.hasn_comments_service import hasn_comments_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的社区评论列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='app_get_my_hasn_comments',
)
async def get_my_hasn_comments(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnCommentsDetail]]:
    page_data = await hasn_comments_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建社区评论',
    dependencies=[DependsJwtAuth],
    name='app_create_my_hasn_comments',
)
async def create_my_hasn_comments(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnCommentsParam,
) -> ResponseModel:
    result = await hasn_comments_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取社区评论详情',
    dependencies=[DependsJwtAuth],
    name='app_get_my_hasn_comments',
)
async def get_my_hasn_comments(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='社区评论 ID')],
) -> ResponseSchemaModel[GetHasnCommentsDetail]:
    hasn_comments = await hasn_comments_service.get(db=db, pk=pk)
    if hasn_comments.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该社区评论')
    return response_base.success(data=hasn_comments)


@router.put(
    '/{pk}',
    summary='更新社区评论',
    dependencies=[DependsJwtAuth],
    name='app_update_my_hasn_comments',
)
async def update_my_hasn_comments(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区评论 ID')],
    obj: UpdateHasnCommentsParam,
) -> ResponseModel:
    hasn_comments = await hasn_comments_service.get(db=db, pk=pk)
    if getattr(hasn_comments, 'user_id', request.user.id) != request.user.id:
        raise errors.ForbiddenError(msg='无权修改该社区评论')
    count = await hasn_comments_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除社区评论',
    dependencies=[DependsJwtAuth],
    name='app_delete_my_hasn_comments',
)
async def delete_my_hasn_comments(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='社区评论 ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_comments = await hasn_comments_service.get(db=db, pk=pk)
    if hasn_comments.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该社区评论')
    from backend.app.hasn.schema.hasn_comments import DeleteHasnCommentsParam
    count = await hasn_comments_service.delete(db=db, obj=DeleteHasnCommentsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
