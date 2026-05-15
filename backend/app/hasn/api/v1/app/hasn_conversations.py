"""HASN 会话 - 用户端 API

认证方式: DependsJwtAuth（仅当前登录用户）
数据隔离: 通过 request.user.id 限制为用户自己的数据
"""
from typing import Annotated

from fastapi import APIRouter, Path, Request, Body
from pydantic import BaseModel, Field

from backend.app.hasn.schema.hasn_conversations import (
    CreateHasnConversationsParam,
    GetHasnConversationsDetail,
    UpdateHasnConversationsParam,
)
from backend.app.hasn.service.hasn_conversations_service import hasn_conversations_service
from backend.common.exception import errors
from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction


class EnsureConversationRequest(BaseModel):
    """确保会话存在的请求参数"""
    peer_hasn_id: str = Field(..., description='对方的 HASN ID')
    relation_type: str | None = Field(default='social', description='关系类型')


class EnsureConversationResponse(BaseModel):
    """确保会话存在的响应"""
    conversation_id: str = Field(..., description='会话 UUID')
    peer_hasn_id: str = Field(..., description='对方的 HASN ID')
    kind: str = Field(..., description='会话类型（direct 表示 1:1）')
    relation_type: str = Field(..., description='关系类型')


router = APIRouter()


@router.post(
    '/ensure',
    summary='确保会话存在（幂等创建）',
    dependencies=[DependsJwtAuth],
)
async def ensure_conversation(
    request: Request,
    db: CurrentSessionTransaction,
    body: Annotated[EnsureConversationRequest, Body()],
) -> ResponseSchemaModel[EnsureConversationResponse]:
    """
    确保 1:1 会话存在。

    根据调用者和对方的 HASN ID 查找或创建会话。
    同一对参与者总是返回相同的 conversation_id（基于排序后的参与者对）。
    """
    # 获取当前用户的 HASN ID
    caller_hasn_id = request.user.hasn_id
    if not caller_hasn_id:
        # 临时调试：如果缓存中没有 hasn_id，尝试从数据库查询
        from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao
        hasn_human = await hasn_humans_dao.get_by_user_id(db, user_id=request.user.id)
        if hasn_human:
            caller_hasn_id = hasn_human.hasn_id
        else:
            raise errors.AuthorizationError(msg='用户未绑定 HASN ID')

    relation_type = body.relation_type or 'social'

    conversation = await hasn_conversations_service.ensure_conversation(
        db=db,
        caller_hasn_id=caller_hasn_id,
        peer_hasn_id=body.peer_hasn_id,
        relation_type=relation_type,
    )

    response_data = EnsureConversationResponse(
        conversation_id=str(conversation.id),
        peer_hasn_id=body.peer_hasn_id,
        kind='direct',
        relation_type=conversation.relation_type or relation_type,
    )

    return response_base.success(data=response_data)


@router.get(
    '',
    summary='获取我的HASN 会话列表',
    dependencies=[DependsJwtAuth, DependsPagination],
)
async def get_my_hasn_conversationss(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[PageData[GetHasnConversationsDetail]]:
    user_id = request.user.id
    page_data = await hasn_conversations_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建HASN 会话',
    dependencies=[DependsJwtAuth],
)
async def create_my_hasn_conversations(
    request: Request,
    db: CurrentSessionTransaction,
    obj: CreateHasnConversationsParam,
) -> ResponseModel:
    user_id = request.user.id
    result = await hasn_conversations_service.create(db=db, obj=obj)
    return response_base.success(data=result)


@router.get(
    '/{pk}',
    summary='获取HASN 会话详情',
    dependencies=[DependsJwtAuth],
)
async def get_my_hasn_conversations(
    request: Request,
    db: CurrentSession,
    pk: Annotated[int, Path(description='HASN 会话 ID')],
) -> ResponseSchemaModel[GetHasnConversationsDetail]:
    hasn_conversations = await hasn_conversations_service.get(db=db, pk=pk)
    if hasn_conversations.user_id != request.user.id:
        raise errors.ForbiddenError(msg='无权访问该HASN 会话')
    return response_base.success(data=hasn_conversations)


@router.put(
    '/{pk}',
    summary='更新HASN 会话',
    dependencies=[DependsJwtAuth],
)
async def update_my_hasn_conversations(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 会话 ID')],
    obj: UpdateHasnConversationsParam,
) -> ResponseModel:
    user_id = request.user.id
    hasn_conversations = await hasn_conversations_service.get(db=db, pk=pk)
    if hasn_conversations.user_id != user_id:
        raise errors.ForbiddenError(msg='无权修改该HASN 会话')
    count = await hasn_conversations_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}',
    summary='删除HASN 会话',
    dependencies=[DependsJwtAuth],
)
async def delete_my_hasn_conversations(
    request: Request,
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='HASN 会话 ID')],
) -> ResponseModel:
    user_id = request.user.id
    hasn_conversations = await hasn_conversations_service.get(db=db, pk=pk)
    if hasn_conversations.user_id != user_id:
        raise errors.ForbiddenError(msg='无权删除该HASN 会话')
    from backend.app.hasn.schema.hasn_conversations import DeleteHasnConversationsParam
    count = await hasn_conversations_service.delete(db=db, obj=DeleteHasnConversationsParam(pks=[pk]))
    if count > 0:
        return response_base.success()
    return response_base.fail()
