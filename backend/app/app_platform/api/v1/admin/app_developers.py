from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_developers import (
    CreateAppDevelopersParam,
    DeleteAppDevelopersParam,
    GetAppDevelopersDetail,
    UpdateAppDevelopersParam,
)
from backend.app.app_platform.service.app_developers_service import app_developers_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取应用开发者详情', dependencies=[DependsJwtAuth], name='admin_get_app_developers')
async def get_app_developers(
    db: CurrentSession, pk: Annotated[int, Path(description='应用开发者 ID')]
) -> ResponseSchemaModel[GetAppDevelopersDetail]:
    app_developers = await app_developers_service.get(db=db, pk=pk)
    return response_base.success(data=app_developers)


@router.get(
    '',
    summary='分页获取所有应用开发者',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_developerss_paginated')
async def get_app_developerss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppDevelopersDetail]]:
    page_data = await app_developers_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建应用开发者',
    dependencies=[
        Depends(RequestPermission('app:developers:add')),
        DependsRBAC,
    ],
)
async def create_app_developers(db: CurrentSessionTransaction, obj: CreateAppDevelopersParam) -> ResponseModel:
    await app_developers_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新应用开发者',
    dependencies=[
        Depends(RequestPermission('app:developers:edit')),
        DependsRBAC,
    ],
)
async def update_app_developers(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='应用开发者 ID')], obj: UpdateAppDevelopersParam
) -> ResponseModel:
    count = await app_developers_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除应用开发者',
    dependencies=[
        Depends(RequestPermission('app:developers:del')),
        DependsRBAC,
    ],
)
async def delete_app_developerss(db: CurrentSessionTransaction, obj: DeleteAppDevelopersParam) -> ResponseModel:
    count = await app_developers_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
