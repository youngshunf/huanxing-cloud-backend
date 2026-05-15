"""
HASN 联系人 & 好友请求 API
对应设计文档: 07-API设计.md §三
阶段二新增: 权限矩阵 API (trust-level / permissions / effective-permissions)
"""
from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException

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
    HasnPermissionsReq,
    AgentPeerOut,
    TRUST_LEVEL_LABELS,
)
from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao
from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn.service.hasn_auth import hasn_auth
from backend.app.hasn.constants import (
    validate_against_iron_laws,
    compute_effective_permissions,
    IronLawViolation,
)

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
    direction: str = Query('received', description='received=收到的, sent=自己发出的'),
) -> ResponseModel:
    """获取待处理好友请求列表。

    - direction=received (默认): 我收到的待处理请求, 每条带 from_peer (发起方)
    - direction=sent: 我已发出但对方还没处理的请求, 每条带 target (目标方)
    """
    if direction not in ('received', 'sent'):
        raise HTTPException(status_code=422, detail="direction 必须是 received 或 sent")

    hasn_id = auth.get("effective_id", auth["hasn_id"])

    if direction == 'received':
        requests = await hasn_contacts_dao.get_pending_requests(db, hasn_id)
        items = []
        for req in requests:
            sender = await hasn_humans_dao.get_by_hasn_id(db, req.owner_id)
            if sender:
                from_peer = HasnContactPeerOut(
                    hasn_id=sender.hasn_id, star_id=sender.star_id,
                    name=sender.name, type='human',
                )
            else:
                # peer_id 解析失败用 stub 占位, 不抛 500 (INV-15)
                from_peer = HasnContactPeerOut(
                    hasn_id=req.owner_id, star_id='', name='', type='human',
                )
            items.append(HasnContactRequestOut(
                request_id=req.id,
                status=req.status,
                from_peer=from_peer,
                message=req.request_message or '',
            ))
        return response_base.success(data=[i.model_dump() for i in items])

    # direction == 'sent'
    requests = await hasn_contacts_dao.get_sent_pending_requests(db, hasn_id)
    items = []
    for req in requests:
        peer_info = await hasn_humans_dao.get_by_hasn_id(db, req.peer_id)
        peer_type = 'human'
        if not peer_info:
            peer_info = await hasn_agents_dao.get_by_hasn_id(db, req.peer_id)
            peer_type = 'agent' if peer_info else 'human'
        if peer_info:
            # HasnHumans 使用 nickname，HasnAgents 使用 display_name
            name = peer_info.nickname if peer_type == 'human' else peer_info.display_name
            target = HasnContactPeerOut(
                hasn_id=peer_info.hasn_id, star_id=peer_info.star_id,
                name=name, type=peer_type,
            )
        else:
            target = HasnContactPeerOut(
                hasn_id=req.peer_id, star_id='', name='', type='human',
            )
        items.append(HasnContactRequestOut(
            request_id=req.id,
            status=req.status,
            target=target,
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

        # 阶段二: 查询 human 联系人名下的 Agent 列表
        owned_agents: list[AgentPeerOut] = []
        if c.peer_type == 'human':
            from sqlalchemy import select
            from backend.app.hasn.model.hasn_agents import HasnAgents
            agent_result = await db.execute(
                select(HasnAgents).where(
                    HasnAgents.owner_id == c.peer_id,
                    HasnAgents.status == 'active',
                )
            )
            for a in agent_result.scalars().all():
                owned_agents.append(AgentPeerOut(
                    hasn_id=a.hasn_id,
                    star_id=a.star_id,
                    name=a.display_name,
                    agent_name=a.agent_name,
                    avatar_url=getattr(a, 'avatar_url', None),
                    type=a.type or 'desktop',
                    role=a.role or 'specialist',
                ))

        # HasnHumans 使用 nickname，HasnAgents 使用 display_name
        peer_name = peer_info.nickname if c.peer_type == 'human' else peer_info.display_name
        items.append(HasnContactOut(
            id=c.id,
            peer=HasnContactPeerOut(
                hasn_id=peer_info.hasn_id,
                star_id=peer_info.star_id,
                name=peer_name,
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
            owned_agents=owned_agents,
            custom_permissions=c.custom_permissions or {},
            scope=c.scope,
            connected_at=str(c.connected_at) if c.connected_at else None,
            last_interaction_at=str(c.last_interaction_at) if c.last_interaction_at else None,
            # Phase 1 US-002: 补齐 contacts 业务字段
            interaction_count=c.interaction_count or 0,
            request_message=c.request_message,
            auto_expire=str(c.auto_expire) if c.auto_expire else None,
            peer_owner_id=c.peer_owner_id,
        ))

    return response_base.success(data=HasnContactListResp(
        total=len(items), items=items
    ).model_dump())


# ─── 阶段二: 权限矩阵 API ───────────────────────────────


@router.put("/{contact_id}/trust-level", summary="修改信任等级")
async def update_trust_level(
    contact_id: int,
    obj_in: HasnTrustLevelReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """
    修改联系人信任等级 (0-5)。
    铁律校验: trust_level=5 仅限自己的 Agent (peer_type='agent')
    """
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    contact = await hasn_contacts_dao.get(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail='联系人不存在')
    if contact.owner_id != hasn_id:
        raise HTTPException(status_code=403, detail='无权修改此联系人')

    # 铁律 2: trust_level=5 仅限自己的 Agent
    if obj_in.trust_level == 5:
        if contact.peer_type != 'agent':
            raise HTTPException(status_code=400, detail='trust_level=5 (所有者) 仅限自己的 Agent')
        # 进一步校验：是否真的是自己的 Agent
        agent = await hasn_agents_dao.get_by_hasn_id(db, contact.peer_id)
        if not agent or agent.owner_id != hasn_id:
            raise HTTPException(status_code=403, detail='只能将自己名下的 Agent 设为所有者等级')

    contact.trust_level = obj_in.trust_level
    await db.commit()

    return response_base.success(data={
        'contact_id': contact_id,
        'trust_level': obj_in.trust_level,
        'trust_level_label': TRUST_LEVEL_LABELS.get(obj_in.trust_level, ''),
    })


@router.put("/{contact_id}/permissions", summary="自定义权限覆盖")
async def update_permissions(
    contact_id: int,
    obj_in: HasnPermissionsReq,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """
    覆盖特定联系人的权限（叠加在默认矩阵之上）。
    系统会对所有覆盖项进行铁律冲突校验，违反任一铁律则拒绝整个请求。
    """
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    contact = await hasn_contacts_dao.get(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail='联系人不存在')
    if contact.owner_id != hasn_id:
        raise HTTPException(status_code=403, detail='无权修改此联系人')

    # 铁律冲突校验
    try:
        validate_against_iron_laws(
            relation_type=contact.relation_type,
            permissions=obj_in.permissions,
            peer_type=contact.peer_type,
            trust_level=contact.trust_level,
        )
    except IronLawViolation as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    # 合并写入（保留未涉及的已有覆盖项）
    existing = contact.custom_permissions or {}
    existing.update(obj_in.permissions)
    contact.custom_permissions = existing
    await db.commit()

    return response_base.success(data={
        'contact_id': contact_id,
        'custom_permissions': contact.custom_permissions,
    })


@router.get("/{contact_id}/effective-permissions", summary="有效权限")
async def get_effective_permissions(
    contact_id: int,
    db: CurrentSession,
    auth: dict = Depends(hasn_auth),
) -> ResponseModel:
    """
    返回合并后的有效权限（默认矩阵 + custom_permissions 覆盖）。
    可用于前端在发起行为前检查权限状态。
    """
    hasn_id = auth.get("effective_id", auth["hasn_id"])
    contact = await hasn_contacts_dao.get(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail='联系人不存在')
    if contact.owner_id != hasn_id:
        raise HTTPException(status_code=403, detail='无权查询此联系人')

    effective = compute_effective_permissions(
        relation_type=contact.relation_type,
        trust_level=contact.trust_level,
        custom_permissions=contact.custom_permissions,
    )

    return response_base.success(data={
        'contact_id': contact_id,
        'relation_type': contact.relation_type,
        'trust_level': contact.trust_level,
        'trust_level_label': TRUST_LEVEL_LABELS.get(contact.trust_level, ''),
        'effective_permissions': effective,
    })
