"""HASN 会话管理端 API"""
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.app.hasn_core.schema.admin.hasn_conversations import (
    CreateHasnConversationParam,
    DeleteHasnConversationParam,
    GetHasnConversationDetail,
    UpdateHasnConversationParam,
)
from backend.app.hasn_core.service.admin.hasn_conversations import hasn_conversations_admin_service
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


@router.get('/{pk}', summary='获取会话详情', dependencies=[DependsJwtAuth])
async def get_hasn_conversations(
    db: CurrentSession, pk: Annotated[str, Path(description='会话 ID')]
) -> ResponseSchemaModel[GetHasnConversationDetail]:
    obj = await hasn_conversations_admin_service.get(db=db, pk=pk)
    return response_base.success(data=obj)


@router.get(
    '',
    summary='分页获取会话列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_hasn_conversations_list(db: CurrentSession) -> ResponseSchemaModel[PageData[GetHasnConversationDetail]]:
    page_data = await hasn_conversations_admin_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建会话',
    dependencies=[Depends(RequestPermission('hasn:conversations:add')), DependsRBAC],
)
async def create_hasn_conversations(db: CurrentSessionTransaction, obj: CreateHasnConversationParam) -> ResponseModel:
    await hasn_conversations_admin_service.create(db=db, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新会话',
    dependencies=[Depends(RequestPermission('hasn:conversations:edit')), DependsRBAC],
)
async def update_hasn_conversations(
    db: CurrentSessionTransaction,
    pk: Annotated[str, Path(description='会话 ID')],
    obj: UpdateHasnConversationParam,
) -> ResponseModel:
    count = await hasn_conversations_admin_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除会话',
    dependencies=[Depends(RequestPermission('hasn:conversations:del')), DependsRBAC],
)
async def delete_hasn_conversations(db: CurrentSessionTransaction, obj: DeleteHasnConversationParam) -> ResponseModel:
    count = await hasn_conversations_admin_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
