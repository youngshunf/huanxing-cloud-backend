from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_tools import (
    CreateAppToolsParam,
    DeleteAppToolsParam,
    GetAppToolsDetail,
    UpdateAppToolsParam,
)
from backend.app.app_platform.service.app_tools_service import app_tools_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取App Tool 定义详情', dependencies=[DependsJwtAuth], name='admin_get_app_tools')
async def get_app_tools(
    db: CurrentSession, pk: Annotated[int, Path(description='App Tool 定义 ID')]
) -> ResponseSchemaModel[GetAppToolsDetail]:
    app_tools = await app_tools_service.get(db=db, pk=pk)
    return response_base.success(data=app_tools)


@router.get(
    '',
    summary='分页获取所有App Tool 定义',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_toolss_paginated')
async def get_app_toolss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppToolsDetail]]:
    page_data = await app_tools_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建App Tool 定义',
    dependencies=[
        Depends(RequestPermission('app:tools:add')),
        DependsRBAC,
    ],
)
async def create_app_tools(db: CurrentSessionTransaction, obj: CreateAppToolsParam) -> ResponseModel:
    await app_tools_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新App Tool 定义',
    dependencies=[
        Depends(RequestPermission('app:tools:edit')),
        DependsRBAC,
    ],
)
async def update_app_tools(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='App Tool 定义 ID')], obj: UpdateAppToolsParam
) -> ResponseModel:
    count = await app_tools_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除App Tool 定义',
    dependencies=[
        Depends(RequestPermission('app:tools:del')),
        DependsRBAC,
    ],
)
async def delete_app_toolss(db: CurrentSessionTransaction, obj: DeleteAppToolsParam) -> ResponseModel:
    count = await app_tools_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
