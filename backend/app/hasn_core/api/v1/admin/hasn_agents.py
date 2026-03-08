"""HASN Agent管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_core.schema.admin.hasn_agents import (
    CreateHasnAgentParam,
    DeleteHasnAgentParam,
    GetHasnAgentDetail,
    UpdateHasnAgentParam,
)
from backend.app.hasn_core.service.admin.hasn_agents import hasn_agents_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取Agent详情', dependencies=[DependsJwtAuth])
async def get_hasn_agents(
    db: CurrentSession, pk: Annotated[str, Path(description='Agent ID')]
) -> ResponseSchemaModel[GetHasnAgentDetail]:
    obj = await hasn_agents_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取Agent列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_agents_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnAgentDetail]]:
    page_data = await hasn_agents_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建Agent',
    dependencies=[Depends(RequestPermission('hasn:agents:add')), DependsRBAC],
)
async def create_hasn_agents(db: CurrentSessionTransaction, obj: CreateHasnAgentParam) -> ResponseModel:
    await hasn_agents_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新Agent',
    dependencies=[Depends(RequestPermission('hasn:agents:edit')), DependsRBAC],
)
async def update_hasn_agents(
    db: CurrentSessionTransaction,
    pk: Annotated[str, Path(description='Agent ID')],
    obj: UpdateHasnAgentParam,
) -> ResponseModel:
    count = await hasn_agents_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除Agent',
    dependencies=[Depends(RequestPermission('hasn:agents:del')), DependsRBAC],
)
async def delete_hasn_agents(db: CurrentSessionTransaction, obj: DeleteHasnAgentParam) -> ResponseModel:
    count = await hasn_agents_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
