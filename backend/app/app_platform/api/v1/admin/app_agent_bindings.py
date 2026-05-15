from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.app_platform.schema.app_agent_bindings import (
    CreateAppAgentBindingsParam,
    DeleteAppAgentBindingsParam,
    GetAppAgentBindingsDetail,
    UpdateAppAgentBindingsParam,
)
from backend.app.app_platform.service.app_agent_bindings_service import app_agent_bindings_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取Installation 绑定的 Agent 列详情', dependencies=[DependsJwtAuth], name='admin_get_app_agent_bindings')
async def get_app_agent_bindings(
    db: CurrentSession, pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')]
) -> ResponseSchemaModel[GetAppAgentBindingsDetail]:
    app_agent_bindings = await app_agent_bindings_service.get(db=db, pk=pk)
    return response_base.success(data=app_agent_bindings)


@router.get(
    '',
    summary='分页获取所有Installation 绑定的 Agent 列',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
 name='admin_get_app_agent_bindingss_paginated')
async def get_app_agent_bindingss_paginated(db: CurrentSession) -> ResponseSchemaModel[PageData[GetAppAgentBindingsDetail]]:
    page_data = await app_agent_bindings_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建Installation 绑定的 Agent 列',
    dependencies=[
        Depends(RequestPermission('app:agent:bindings:add')),
        DependsRBAC,
    ],
)
async def create_app_agent_bindings(db: CurrentSessionTransaction, obj: CreateAppAgentBindingsParam) -> ResponseModel:
    await app_agent_bindings_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新Installation 绑定的 Agent 列',
    dependencies=[
        Depends(RequestPermission('app:agent:bindings:edit')),
        DependsRBAC,
    ],
)
async def update_app_agent_bindings(
    db: CurrentSessionTransaction, pk: Annotated[int, Path(description='Installation 绑定的 Agent 列 ID')], obj: UpdateAppAgentBindingsParam
) -> ResponseModel:
    count = await app_agent_bindings_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除Installation 绑定的 Agent 列',
    dependencies=[
        Depends(RequestPermission('app:agent:bindings:del')),
        DependsRBAC,
    ],
)
async def delete_app_agent_bindingss(db: CurrentSessionTransaction, obj: DeleteAppAgentBindingsParam) -> ResponseModel:
    count = await app_agent_bindings_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
