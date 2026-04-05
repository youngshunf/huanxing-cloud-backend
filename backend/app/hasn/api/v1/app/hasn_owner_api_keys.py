"""HASN Owner API Key  - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request

from backend.app.hasn.schema.hasn_owner_api_keys import (
    CreateHasnOwnerApiKeysParam,
    GetHasnOwnerApiKeysDetail,
    UpdateHasnOwnerApiKeysParam,
)
from backend.app.hasn.service.hasn_owner_api_keys_service import hasn_owner_api_keys_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get(
    '',
    summary='获取我的HASN Owner API Key 列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_hasn_owner_api_keyss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnOwnerApiKeysDetail]]:
    user_id = request.user.id
    page_data = await hasn_owner_api_keys_service.get_list(db=db, user_id=user_id)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN Owner API Key ',
    dependencies=[DependsJwtAuth],
)
async def create_my_hasn_owner_api_keys(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnOwnerApiKeysParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await hasn_owner_api_keys_service.create(db=db, obj=obj, user_id=user_id)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN Owner API Key 详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_hasn_owner_api_keys(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN Owner API Key  ID')],
) -> ResponseSchemaModel[GetHasnOwnerApiKeysDetail]:
    hasn_owner_api_keys = await hasn_owner_api_keys_service.get(db=db, pk=pk)
    if hasn_owner_api_keys.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该HASN Owner API Key ')
    return response_base.success(data=hasn_owner_api_keys)


@router.put(
    '/{pk}',
    summary='更新HASN Owner API Key ',
    dependencies=[DependsJwtAuth],
)
async def update_my_hasn_owner_api_keys(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Owner API Key  ID')],
    obj: UpdateHasnOwnerApiKeysParam,
) -> ResponseModel:
    user_id = request.user.id
    hasn_owner_api_keys = await hasn_owner_api_keys_service.get(db=db, pk=pk)
    if hasn_owner_api_keys.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN Owner API Key ')
    count = await hasn_owner_api_keys_service.update(db=db, pk=pk, obj=obj, user_id=user_id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN Owner API Key ',
    dependencies=[DependsJwtAuth],
)
async def delete_my_hasn_owner_api_keys(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN Owner API Key  ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_owner_api_keys = await hasn_owner_api_keys_service.get(db=db, pk=pk)
    if hasn_owner_api_keys.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN Owner API Key ')
    from backend.app.hasn.schema.hasn_owner_api_keys import DeleteHasnOwnerApiKeysParam
    count = await hasn_owner_api_keys_service.delete(db=db, obj=DeleteHasnOwnerApiKeysParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
