"""
HASN 会话列表 & 消息历史 & 已读 & 未读数 API
对应设计文档: 07-API设计.md §四
"""
from fastapi import APIRouter, Depends, Path, Query

from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.response.response_code import CustomResponse
from backend.database.db import CurrentSession
from backend.database.redis import redis_client
from backend.app.hasn_core.service.hasn_auth import hasn_auth
from backend.app.hasn_core.crud.crud_human import crud_hasn_human
from backend.app.hasn_core.crud.crud_agent import crud_hasn_agent
from backend.app.hasn_core.crud.crud_conversation import crud_hasn_conversation
from backend.app.hasn_core.crud.crud_message import crud_hasn_message

router = APIRouter(prefix="/conversations", tags=["HASN Conversations"])


@router.get("", summary="会话列表")
async def list_conversations(
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ResponseModel:
    """返回当前用户参与的所有会话，按最后消息时间倒序"""
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    convs = await crud_hasn_conversation.list_for_user(db, hasn_id, limit=limit, offset=offset)

    items = []
    for conv in convs:
        # 确定对方是谁
        peer_id = conv.participant_b if conv.participant_a == hasn_id else conv.participant_a
        if not peer_id:
            continue

        # 查对方信息
        peer = await crud_hasn_human.get_by_id(db, peer_id)
        peer_type = "human"
        if not peer:
            peer = await crud_hasn_agent.get_by_id(db, peer_id)
            peer_type = "agent"

        # 获取未读数
        unread_raw = await redis_client.hget(f"hasn:unread:{hasn_id}", conv.id)
        unread = int(unread_raw) if unread_raw else 0

        items.append({
            "id": conv.id,
            "type": conv.type,
            "peer": {
                "hasn_id": peer.id if peer else peer_id,
                "star_id": peer.star_id if peer else "",
                "name": peer.name if peer else "未知",
                "type": peer_type,
                "avatar_url": getattr(peer, 'avatar_url', None) if peer else None,
            },
            "last_message_at": str(conv.last_message_at) if conv.last_message_at else None,
            "last_message_preview": conv.last_message_preview,
            "message_count": conv.message_count,
            "unread": unread,
            "status": conv.status,
        })

    return response_base.success(data={"total": len(items), "items": items})


@router.get("/unread", summary="未读消息计数")
async def get_unread_counts(
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """返回所有会话的未读计数 {conversation_id: count}"""
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    raw = await redis_client.hgetall(f"hasn:unread:{hasn_id}")
    counts = {}
    if raw:
        for k, v in raw.items():
            key = k.decode() if isinstance(k, bytes) else str(k)
            val = v.decode() if isinstance(v, bytes) else str(v)
            counts[key] = int(val)
    return response_base.success(data=counts)


@router.get("/{conversation_id}/messages", summary="消息历史")
async def get_messages(
    db: CurrentSession,
    conversation_id: str = Path(...),
    auth: dict = Depends(hasn_auth),
    before_id: int | None = Query(None, description="游标: 返回此ID之前的消息"),
    limit: int = Query(50, ge=1, le=100),
) -> ResponseModel:
    """按 BIGINT id 倒序分页，游标翻页"""
    hasn_id = auth.get("effective_id", auth["hasn_id"])

    # 验证用户是否属于该会话
    conv = await crud_hasn_conversation.get_by_id(db, conversation_id)
    if not conv:
        return response_base.fail(res=CustomResponse(code=400, msg="会话不存在"))
    if hasn_id not in (conv.participant_a, conv.participant_b):
        return response_base.fail(res=CustomResponse(code=400, msg="无权访问此会话"))

    messages = await crud_hasn_message.get_by_conversation(
        db, conversation_id, before_id=before_id, limit=limit)

    items = [{
        "id": msg.id,
        "conversation_id": msg.conversation_id,
        "from_id": msg.from_id,
        "from_type": msg.from_type,
        "content_type": msg.content_type,
        "content": msg.content,
        "status": msg.status,
        "created_at": str(msg.created_time) if msg.created_time else None,
    } for msg in messages]

    return response_base.success(data={
        "items": items,
        "has_more": len(items) == limit,
    })


@router.post("/{conversation_id}/read", summary="标记已读")
async def mark_read(
    db: CurrentSession,
    conversation_id: str = Path(...),
    auth: dict = Depends(hasn_auth),
    last_msg_id: int = Query(..., description="已读到的最后一条消息ID"),
) -> ResponseModel:
    hasn_id = auth.get("effective_id", auth["hasn_id"])

    # 验证会话归属
    conv = await crud_hasn_conversation.get_by_id(db, conversation_id)
    if not conv or hasn_id not in (conv.participant_a, conv.participant_b):
        return response_base.fail(res=CustomResponse(code=400, msg="无权操作此会话"))

    # 标记已读
    await crud_hasn_message.mark_read(db, conversation_id, last_msg_id)
    await db.commit()

    # 清除未读数
    await redis_client.hdel(f"hasn:unread:{hasn_id}", conversation_id)

    return response_base.success(data={
        "conversation_id": conversation_id,
        "read_to": last_msg_id,
    })


@router.get("/presence/{star_id}", summary="在线状态查询")
async def check_presence(
    star_id: str = Path(...),
    db: CurrentSession = None,
) -> ResponseModel:
    """查询某唤星号是否在线"""
    from backend.app.hasn_core.service.ws_router import ws_router

    # 先解析 star_id → hasn_id
    if db:
        entity = await crud_hasn_human.get_by_star_id(db, star_id)
        if not entity:
            entity = await crud_hasn_agent.get_by_star_id(db, star_id)
        if not entity:
            return response_base.fail(res=CustomResponse(code=400, msg=f"唤星号 {star_id} 不存在"))
        online = await ws_router.is_online(entity.id)
        return response_base.success(data={
            "star_id": star_id,
            "online": online,
        })

    return response_base.success(data={"star_id": star_id, "online": False})
