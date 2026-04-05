"""HASN Node Owner Binding 租约 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_node_bindings import (
    CreateHasnNodeBindingsParam,
    GetHasnNodeBindingsDetail,
    UpdateHasnNodeBindingsParam,
)
from backend.app.hasn.service.hasn_node_bindings_service import hasn_node_bindings_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的HASN Node Owner Binding 租约列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_hasn_node_bindingss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnNodeBindingsDetail]]:
    user_id = request.user.id
    page_data = await hasn_node_bindings_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN Node Owner Binding 租约',
    dependencies=[DependsJwtAuth],
)
async def create_my_hasn_node_bindings(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnNodeBindingsParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await hasn_node_bindings_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN Node Owner Binding 租约详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_hasn_node_bindings(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Node Owner Binding 租约 ID')],
) -> ResponseSchemaModel[GetHasnNodeBindingsDetail]:
    hasn_node_bindings = await hasn_node_bindings_service.get(db=db, pk=pk)
    if hasn_node_bindings.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该HASN Node Owner Binding 租约')
    return response_base.success(data=hasn_node_bindings)


@router.put(
    '/{pk}',
    summary='更新HASN Node Owner Binding 租约',
    dependencies=[DependsJwtAuth],
)
async def update_my_hasn_node_bindings(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Node Owner Binding 租约 ID')],
    obj: UpdateHasnNodeBindingsParam,
) -> ResponseModel:
    user_id = request.user.id
    hasn_node_bindings = await hasn_node_bindings_service.get(db=db, pk=pk)
    if hasn_node_bindings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Node Owner Binding 租约')
    count = await hasn_node_bindings_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN Node Owner Binding 租约',
    dependencies=[DependsJwtAuth],
)
async def delete_my_hasn_node_bindings(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Node Owner Binding 租约 ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_node_bindings = await hasn_node_bindings_service.get(db=db, pk=pk)
    if hasn_node_bindings.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Node Owner Binding 租约')
    from backend.app.hasn.schema.hasn_node_bindings import DeleteHasnNodeBindingsParam
    count = await hasn_node_bindings_service.delete(db=db, obj=DeleteHasnNodeBindingsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
