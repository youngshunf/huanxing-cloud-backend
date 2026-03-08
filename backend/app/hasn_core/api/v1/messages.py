"""
HASN 消息发送 API
对应设计文档: 07-API设计.md §四
"""
import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.common.log import log
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.response.response_code import CustomResponse
from backend.database.db import CurrentSession
from backend.database.redis import redis_client
from backend.app.hasn_core.service.hasn_auth import hasn_auth
from backend.app.hasn_core.crud.crud_human import crud_hasn_human
from backend.app.hasn_core.crud.crud_agent import crud_hasn_agent
from backend.app.hasn_core.crud.crud_message import crud_hasn_message
from backend.app.hasn_core.crud.crud_conversation import crud_hasn_conversation
from backend.app.hasn_social.service.route_guard import route_guard
from backend.app.hasn_core.service.ws_router import ws_router

router = APIRouter(prefix="/messages", tags=["HASN Messages"])


# ── Schema ────────────────────────────

class HasnSendMessageReq(BaseModel):
    to: str = Field(..., description="目标唤星号")
    content: str = Field(..., min_length=1, max_length=10000)
    content_type: int = Field(1, description="1=text 2=image 3=file 4=voice 5=rich 6=capability")


class HasnMessageOut(BaseModel):
    id: int
    conversation_id: str
    from_id: str
    from_type: int
    content: str
    content_type: int
    status: int
    created_at: str | None = None


# ── 工具函数 ──────────────────────────

async def _resolve_target(db, star_id: str):
    """
    解析唤星号 → (实体, 类型, 权限检查用的owner_id)

    - Human (100001) → (human, "human", human.id)
    - Agent (100001#star) → (agent, "agent", agent.owner_id)
    """
    if '#' in star_id:
        agent = await crud_hasn_agent.get_by_star_id(db, star_id)
        if agent:
            return agent, 'agent', agent.owner_id
    else:
        human = await crud_hasn_human.get_by_star_id(db, star_id)
        if human:
            return human, 'human', human.id
    return None, None, None


def _get_permission_pair(
    sender_type: str,
    sender_id: str,
    sender_owner_id: str | None,
    target_type: str,
    target_owner_id: str,
) -> tuple[str, str]:
    """
    计算权限检查用的两个 hasn_id (必须是 human 之间的关系)

    H→H: sender_id, target_id
    H→A: sender_id, agent.owner_id
    A→H: agent.owner_id, target_id
    A→A: sender.owner_id, target.owner_id
    """
    s = sender_owner_id if sender_type == 'agent' and sender_owner_id else sender_id
    t = target_owner_id
    return s, t


# ── API ───────────────────────────────

@router.post("/send", summary="发送消息")
async def send_message(
    obj_in: HasnSendMessageReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """
    通过 REST 发送消息。

    流程: 认证 → 解析目标 → 权限检查 → 创建会话 → 写消息 → WS推送/离线入队
    """
    hasn_id = auth["hasn_id"]  # 消息的 from_id 必须是实际发送者 (agent 或 human)
    entity_type = auth["type"]

    # 1. 解析目标
    target, target_type, target_owner_id = await _resolve_target(db, obj_in.to)
    if not target:
        return response_base.fail(res=CustomResponse(code=400, msg=f"唤星号 {obj_in.to} 不存在"))

    # 不能给自己发消息
    if target.id == hasn_id:
        return response_base.fail(res=CustomResponse(code=400, msg="不能给自己发消息"))

    # 2. 获取发送者 owner_id (agent 需要)
    sender_owner_id = None
    if entity_type == "agent":
        sender_entity = await crud_hasn_agent.get_by_id(db, hasn_id)
        if sender_entity:
            sender_owner_id = sender_entity.owner_id

    # 3. 权限检查 (human-to-human 维度)
    perm_sender, perm_receiver = _get_permission_pair(
        entity_type, hasn_id, sender_owner_id, target_type, target_owner_id)

    # 同一个 human 的 agent 给自己发消息 → 直接放行
    if perm_sender != perm_receiver:
        allowed = await route_guard.check_permission(db, perm_sender, perm_receiver)
        if not allowed:
            return response_base.fail(res=CustomResponse(code=400, msg=f"没有权限给 {obj_in.to} 发消息，请先添加好友"))

    # 4. 获取/创建会话
    conv = await crud_hasn_conversation.get_or_create_direct(db, hasn_id, target.id)

    # 5. 创建消息 (from_type: 1=human 2=agent 3=system)
    from_type = 1 if entity_type == "human" else 2
    msg = await crud_hasn_message.create(
        db,
        conversation_id=conv.id,
        from_id=hasn_id,
        from_type=from_type,
        content=obj_in.content,
        content_type=obj_in.content_type,
    )

    # 6. 更新会话最后消息
    await crud_hasn_conversation.update_last_message(db, conv.id, obj_in.content)
    await db.commit()
    await db.refresh(msg)

    # 7. WS推送 / 离线入队
    msg_payload = json.dumps({
        "type": "hasn_message",
        "message": {
            "id": msg.id,
            "conversation_id": conv.id,
            "from_id": hasn_id,
            "from_star_id": auth["star_id"],
            "from_type": from_type,
            "content": obj_in.content,
            "content_type": obj_in.content_type,
            "created_at": str(msg.created_time) if msg.created_time else None,
        },
    })

    target_sid = await ws_router.get_client_sid(target.id)
    if target_sid:
        await redis_client.rpush(f"hasn:push:{target.id}", msg_payload)
        log.info(f"[HASN MSG] 在线推送: {hasn_id} -> {target.id} msg_id={msg.id}")
    else:
        await redis_client.rpush(f"hasn:offline:{target.id}", msg_payload)
        await redis_client.expire(f"hasn:offline:{target.id}", 7 * 86400)
        log.info(f"[HASN MSG] 离线入队: {hasn_id} -> {target.id} msg_id={msg.id}")

    # 8. 更新未读数
    await redis_client.hincrby(f"hasn:unread:{target.id}", conv.id, 1)

    return response_base.success(data=HasnMessageOut(
        id=msg.id,
        conversation_id=conv.id,
        from_id=hasn_id,
        from_type=from_type,
        content=obj_in.content,
        content_type=obj_in.content_type,
        status=1,
        created_at=str(msg.created_time) if msg.created_time else None,
    ).model_dump())
