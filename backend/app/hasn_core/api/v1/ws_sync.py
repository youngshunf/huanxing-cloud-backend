"""
HASN 离线消息补齐接口
对应设计文档: 02-通信协议.md §3.5
"""
from fastapi import APIRouter

from backend.common.response.response_schema import ResponseModel, response_base
from backend.database.db import CurrentSession
from backend.app.hasn_core.crud.crud_message import crud_hasn_message
from backend.app.hasn_core.crud.crud_conversation import crud_hasn_conversation

router = APIRouter(prefix="/ws", tags=["HASN WS Sync"])


@router.get("/sync", summary="离线消息补齐")
async def sync_messages(
    db: CurrentSession,
    conversation_id: str,
    last_msg_id: int | None = None,
    limit: int = 50,
) -> ResponseModel:
    """
    客户端断线重连后，根据最后收到的消息ID拉取遗漏消息。
    对应设计文档: 消息表使用 BIGINT 自增 id，天然有序。
    """
    messages = await crud_hasn_message.get_by_conversation(
        db,
        conversation_id=conversation_id,
        before_id=None,  # 取最新的
        limit=limit,
    )

    # 只返回 > last_msg_id 的消息
    if last_msg_id is not None:
        messages = [m for m in messages if m.id > last_msg_id]

    return response_base.success(data=[{
        "id": msg.id,
        "conversation_id": msg.conversation_id,
        "from_id": msg.from_id,
        "from_type": msg.from_type,
        "content_type": msg.content_type,
        "content": msg.content,
        "status": msg.status,
        "created_at": str(msg.created_time) if msg.created_time else None,
    } for msg in messages])
