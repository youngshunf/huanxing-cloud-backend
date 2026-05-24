"""任务系统 Session API

用于任务系统的 Session 管理，包括：
- Session 创建/更新（upsert）
- Session 摘要更新
- Session 关闭
- Session 消息查询和发送
"""
from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field

from backend.app.hasn.service.hasn_sessions_service import hasn_sessions_service
from backend.common.pagination import DependsPagination
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.database.db import CurrentSession, CurrentSessionTransaction

router = APIRouter()


class SessionUpsertRequest(BaseModel):
    """Session Upsert 请求"""
    session_id: str = Field(..., description="Session ID (ULID)")
    conversation_id: str | None = Field(None, description="会话 ID")
    owner_id: str = Field(..., description="Owner ID")
    hasn_id: str = Field(..., description="Agent ID")
    session_kind: str = Field(..., description="Session 类型")
    session_scope: str = Field(..., description="同步范围")
    session_status: str = Field(default="active", description="Session 状态")
    parent_session_id: str | None = Field(None, description="父 Session ID")
    continuation_from_session_id: str | None = Field(None, description="续接自哪个 Session")
    origin_type: str = Field(..., description="来源类型")
    origin_ref: str | None = Field(None, description="来源引用")
    title: str | None = Field(None, description="Session 标题")
    summary_checkpoint_json: dict | None = Field(default={}, description="摘要快照")
    active_binding_id: str | None = Field(None, description="当前活跃的绑定 ID")


class SessionSummaryUpdateRequest(BaseModel):
    """Session 摘要更新请求"""
    summary_checkpoint_json: dict = Field(..., description="摘要快照")
    last_message_at: str | None = Field(None, description="最后消息时间")


class SessionCloseRequest(BaseModel):
    """Session 关闭请求"""
    session_status: str = Field(default="completed", description="关闭状态")


class SessionMessageSendRequest(BaseModel):
    """Session 消息发送请求"""
    content_text: str = Field(..., description="消息内容")
    client_message_id: str = Field(..., description="客户端消息 ID")


@router.post(
    '/sessions/upsert',
    summary='创建或更新 Session',
    dependencies=[DependsJwtAuth],
    name='hasn_session_upsert',
)
async def session_upsert(
    request: Request,
    db: CurrentSessionTransaction,
    obj: SessionUpsertRequest,
) -> ResponseModel:
    """创建或更新 Session（幂等操作）"""
    session = await hasn_sessions_service.upsert(db=db, session_data=obj.model_dump())
    return response_base.success(data={'session_id': session.session_id})


@router.post(
    '/sessions/{session_id}/summary',
    summary='更新 Session 摘要',
    dependencies=[DependsJwtAuth],
    name='hasn_session_update_summary',
)
async def session_update_summary(
    request: Request,
    db: CurrentSessionTransaction,
    session_id: Annotated[str, Path(description="Session ID")],
    obj: SessionSummaryUpdateRequest,
) -> ResponseModel:
    """更新 Session 摘要"""
    session = await hasn_sessions_service.update_summary(
        db=db,
        session_id=session_id,
        summary_data=obj.model_dump()
    )
    return response_base.success(data={'session_id': session.session_id})


@router.post(
    '/sessions/{session_id}/close',
    summary='关闭 Session',
    dependencies=[DependsJwtAuth],
    name='hasn_session_close',
)
async def session_close(
    request: Request,
    db: CurrentSessionTransaction,
    session_id: Annotated[str, Path(description="Session ID")],
    obj: SessionCloseRequest,
) -> ResponseModel:
    """关闭 Session"""
    session = await hasn_sessions_service.close_session(
        db=db,
        session_id=session_id,
        close_data=obj.model_dump()
    )
    return response_base.success(data={'session_id': session.session_id})


@router.get(
    '/sessions',
    summary='查询 Session 列表',
    dependencies=[DependsJwtAuth, DependsPagination],
    name='hasn_session_list',
)
async def session_list(
    request: Request,
    db: CurrentSession,
    session_kind: Annotated[str | None, Query(description="Session 类型，逗号分隔")] = None,
    session_scope: Annotated[str | None, Query(description="同步范围")] = None,
    session_status: Annotated[str | None, Query(description="Session 状态")] = None,
) -> ResponseModel:
    """查询 Session 列表"""
    # TODO: 实现过滤逻辑
    page_data = await hasn_sessions_service.get_list(db=db)
    return response_base.success(data=page_data)


@router.get(
    '/sessions/{session_id}/messages',
    summary='查询 Session 消息列表',
    dependencies=[DependsJwtAuth],
    name='hasn_session_messages',
)
async def session_messages(
    request: Request,
    db: CurrentSession,
    session_id: Annotated[str, Path(description="Session ID")],
    page: Annotated[int, Query(description="页码", ge=1)] = 1,
    page_size: Annotated[int, Query(description="每页数量", ge=1, le=100)] = 50,
) -> ResponseModel:
    """查询 Session 消息列表"""
    # TODO: 从 hasn_messages 表查询消息
    return response_base.success(data={'messages': [], 'total': 0})


@router.post(
    '/sessions/{session_id}/messages',
    summary='发送消息到 Session',
    dependencies=[DependsJwtAuth],
    name='hasn_session_send_message',
)
async def session_send_message(
    request: Request,
    db: CurrentSessionTransaction,
    session_id: Annotated[str, Path(description="Session ID")],
    obj: SessionMessageSendRequest,
) -> ResponseModel:
    """发送消息到 Session"""
    # TODO: 路由到 hasn-node 执行
    return response_base.success(data={'message_id': 'msg_placeholder'})
