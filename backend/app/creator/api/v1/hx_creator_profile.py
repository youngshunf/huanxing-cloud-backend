from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.creator.schema.hx_creator_profile import (
    CreateHxCreatorProfileParam,
    DeleteHxCreatorProfileParam,
    GetHxCreatorProfileDetail,
    UpdateHxCreatorProfileParam,
)
from backend.app.creator.service.hx_creator_profile_service import hx_creator_profile_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取账号画像详情', dependencies=[DependsJwtAuth])
async def get_hx_creator_profile(
    db: CurrentSession, pk: Annotated[int, Path(description='账号画像 ID')]
) -> ResponseSchemaModel[GetHxCreatorProfileDetail]:
    hx_creator_profile = await hx_creator_profile_service.get(db=db, pk=pk)
    return response_base.success(data=hx_creator_profile)


@router.get(
    '',
    summary='分页获取所有账号画像',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_hx_creator_profiles_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHxCreatorProfileDetail]]:
    page_data = await hx_creator_profile_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建账号画像',
    dependencies=[
        Depends(RequestPermission('hx:creator:profile:add')),
        DependsRBAC,
    ],
)
async def create_hx_creator_profile(db: CurrentSessionTransaction, obj: CreateHxCreatorProfileParam) -> ResponseModel:
    await hx_creator_profile_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新账号画像',
    dependencies=[
        Depends(RequestPermission('hx:creator:profile:edit')),
        DependsRBAC,
    ],
)
async def update_hx_creator_profile(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='账号画像 ID')], obj: UpdateHxCreatorProfileParam
) -> ResponseModel:
    count = await hx_creator_profile_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除账号画像',
    dependencies=[
        Depends(RequestPermission('hx:creator:profile:del')),
        DependsRBAC,
    ],
)
async def delete_hx_creator_profiles(db: CurrentSessionTransaction, obj: DeleteHxCreatorProfileParam) -> ResponseModel:
    count = await hx_creator_profile_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
