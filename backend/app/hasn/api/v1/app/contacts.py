"""
HASN 联系人 & 好友请求 API
对应设计文档: 07-API设计.md §三
"""
from fastapi import APIRouter, Depends, Query

from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.response.response_code import CustomResponse
from backend.database.db import CurrentSession
from backend.app.hasn.crud.crud_hasn_contacts import hasn_contacts_dao
from backend.app.hasn.schema.hasn_contacts_business import (
    HasnContactRequestReq,
    HasnContactRespondReq,
    HasnContactPeerOut,
    HasnContactRequestOut,
    HasnContactOut,
    HasnContactListResp,
    HasnTrustLevelReq,
    TRUST_LEVEL_LABELS,
)
from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao
from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn.service.hasn_auth import hasn_auth

router = APIRouter(prefix="/contacts", tags=["HASN Contacts"])


async def _resolve_star_id(db, star_id: str):
    """解析唤星号 → 实体 (human 或 agent)"""
    if '#' in star_id:
        agent = await hasn_agents_dao.get_by_star_id(db, star_id)
        if agent:
            return agent, 'agent'
    else:
        human = await hasn_humans_dao.get_by_star_id(db, star_id)
        if human:
            return human, 'human'
    return None, None


@router.post("/request", summary="发送好友请求")
async def send_contact_request(
    obj_in: HasnContactRequestReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """发送好友请求 (social 关系)"""
    hasn_id = auth.get("effective_id", auth["hasn_id"])

    # 解析目标
    target, target_type = await _resolve_star_id(db, obj_in.target_star_id)
    if not target:
        return response_base.fail(res=CustomResponse(code=400, msg=f"唤星号 {obj_in.target_star_id} 不存在"))

    # 检查是否已有关系（使用 hasn_id）
    existing = await hasn_contacts_dao.get_relation(db, hasn_id, target.hasn_id, 'social')
    if existing:
        return response_base.fail(res=CustomResponse(code=400, msg=f"与 {obj_in.target_star_id} 已存在关系 (status={existing.status})"))

    # 创建 pending 关系
    contact = await hasn_contacts_dao.create_contact(
        db,
        owner_id=hasn_id,
        peer_id=target.hasn_id,
        peer_type=target_type,
        relation_type='social',
        trust_level=1,
        status='pending',
        request_message=obj_in.message,
    )
    await db.commit()

    return response_base.success(data=HasnContactRequestOut(
        request_id=contact.id,
        status='pending',
        target=HasnContactPeerOut(
            hasn_id=target.hasn_id,
            star_id=target.star_id,
            name=target.name,
            type=target_type,
        ),
        message=obj_in.message,
    ).model_dump())


@router.get("/requests", summary="获取待处理好友请求")
async def list_pending_requests(
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    requests = await hasn_contacts_dao.get_pending_requests(db, hasn_id)
    items = []
    for req in requests:
        sender = await hasn_humans_dao.get_by_hasn_id(db, req.owner_id)
        from_peer = None
        if sender:
            from_peer = HasnContactPeerOut(
                hasn_id=sender.hasn_id, star_id=sender.star_id,
                name=sender.name, type='human',
            )
        items.append(HasnContactRequestOut(
            request_id=req.id,
            status=req.status,
            from_peer=from_peer,
            message=req.request_message or '',
        ))
    return response_base.success(data=[i.model_dump() for i in items])


@router.put("/requests/{request_id}/respond", summary="回应好友请求")
async def respond_to_request(
    request_id: int,
    obj_in: HasnContactRespondReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """接受/拒绝好友请求"""
    if obj_in.action == 'accept':
        await hasn_contacts_dao.accept_request(db, request_id)

        # 查出原请求并创建反向关系
        contact = await hasn_contacts_dao.get(db, request_id)
        if contact:
            existing_reverse = await hasn_contacts_dao.get_relation(
                db, contact.peer_id, contact.owner_id, 'social')
            if not existing_reverse:
                await hasn_contacts_dao.create_contact(
                    db,
                    owner_id=contact.peer_id,
                    peer_id=contact.owner_id,
                    peer_type='human',
                    relation_type='social',
                    trust_level=2,
                    status='connected',
                )
        await db.commit()
        return response_base.success(data={"status": "connected", "trust_level": 2})

    elif obj_in.action == 'reject':
        await hasn_contacts_dao.reject_request(db, request_id)
        await db.commit()
        return response_base.success(data={"status": "rejected"})

    return response_base.fail(res=CustomResponse(code=400, msg="action 必须是 accept 或 reject"))


@router.get("", summary="联系人列表")
async def list_contacts(
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
    relation_type: str = Query('social', description='关系类型筛选'),
) -> ResponseModel:
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    contacts = await hasn_contacts_dao.list_contacts(
        db, hasn_id, relation_type=relation_type)

    items = []
    for c in contacts:
        # 查 peer 信息（使用 hasn_id）
        peer_info = await hasn_humans_dao.get_by_hasn_id(db, c.peer_id)
        if not peer_info:
            peer_info = await hasn_agents_dao.get_by_hasn_id(db, c.peer_id)
        if not peer_info:
            continue

        items.append(HasnContactOut(
            id=c.id,
            peer=HasnContactPeerOut(
                hasn_id=peer_info.hasn_id,
                star_id=peer_info.star_id,
                name=peer_info.name,
                type=c.peer_type,
                avatar_url=getattr(peer_info, 'avatar_url', None),
            ),
            relation_type=c.relation_type,
            trust_level=c.trust_level,
            trust_level_label=TRUST_LEVEL_LABELS.get(c.trust_level, ''),
            nickname=c.nickname,
            tags=c.tags,
            subscription=c.subscription,
            status=c.status,
            connected_at=str(c.connected_at) if c.connected_at else None,
            last_interaction_at=str(c.last_interaction_at) if c.last_interaction_at else None,
        ))

    return response_base.success(data=HasnContactListResp(
        total=len(items), items=items
    ).model_dump())
