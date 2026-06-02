"""
HASN 联系人 & 好友请求 API
对应设计文档: 07-API设计.md §三
阶段二新增: 权限矩阵 API (trust-level / permissions / effective-permissions)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.admin.crud.crud_user import user_dao
from backend.app.hasn.constants import (
    ERR_TRUST_LEVEL_INVALID,
    IronLawViolation,
    compute_effective_permissions,
    validate_against_iron_laws,
    validate_relation_constraints,
)
from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn.crud.crud_hasn_contact_requests import hasn_contact_requests_dao
from backend.app.hasn.crud.crud_hasn_contacts import hasn_contacts_dao
from backend.app.hasn.crud.crud_hasn_humans import hasn_humans_dao
from backend.app.hasn.schema.hasn_contacts_business import (
    TRUST_LEVEL_LABELS,
    AgentPeerOut,
    HasnContactListResp,
    HasnContactOut,
    HasnContactPeerOut,
    HasnContactRequestOut,
    HasnContactRequestReq,
    HasnContactRespondReq,
    HasnPermissionsReq,
    HasnTrustLevelReq,
)
from backend.app.hasn.service.hasn_auth import hasn_auth
from backend.app.hasn.service.hasn_contacts_service import HasnContactsService
from backend.app.hasn.service.ws_router import ws_router
from backend.common.response.response_code import CustomResponse
from backend.common.response.response_schema import ResponseModel, response_base
from backend.database.db import CurrentSession

router = APIRouter(prefix='/contacts', tags=['HASN Contacts'])


def _peer_display_name(peer_info, *, peer_type: str) -> str:
    if peer_type == 'human':
        return getattr(peer_info, 'nickname', None) or getattr(peer_info, 'name', '') or ''
    return getattr(peer_info, 'display_name', None) or getattr(peer_info, 'name', '') or ''


async def _resolve_peer_user_profile(db, peer_info, *, peer_type: str):
    if peer_type != 'human':
        return None
    user_id = getattr(peer_info, 'user_id', None)
    if not user_id:
        return None
    return await user_dao.get(db, user_id)


async def _push_contact_event(target_hasn_id: str, payload: dict) -> None:
    try:
        await ws_router.push_message_to(target_hasn_id, payload)
    except Exception:
        return


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


def _agent_peer_out(agent) -> HasnContactPeerOut:
    """把一个 HasnAgents 行整形成 type='agent' 的 peer 输出（列表/请求/连接事件复用）。"""
    return HasnContactPeerOut(
        hasn_id=agent.hasn_id,
        star_id=getattr(agent, 'star_id', '') or '',
        name=_peer_display_name(agent, peer_type='agent'),
        type='agent',
        avatar=getattr(agent, 'avatar', None),
    )


async def _send_agent_contact_request(db, *, requester_id: str, agent, message: str | None, add_source: str = 'other'):
    """普通朋友请求把好友的『分身』加为联系人（agent 目标，审批人=分身主人）。

    与 human 目标的本质区别：目标保持为分身本体（to_type='agent'、to_id=分身 hasn_id），
    审批人是分身主人。主人是好友是本流程的前置，不再当作"已是好友"冲突拦截。
    通过后请求方获得一条 peer_type='agent' 的 social 边，信任等级与『请求方↔主人』一致。
    """
    agent_id = agent.hasn_id
    owner_id = getattr(agent, 'owner_id', None) or agent_id
    msg_text = message or ''

    if owner_id == requester_id:
        return response_base.fail(res=CustomResponse(code=400, msg='不能添加自己的分身'))

    # 已是该分身的联系人（agent 级 connected 边）
    existing = await hasn_contacts_dao.get_relation(db, requester_id, agent_id, 'social')
    if existing and existing.status == 'connected':
        return response_base.fail(res=CustomResponse(code=400, msg='你已添加该分身'))

    # 被分身主人拉黑（主人 → 我 方向 trust_level=0）
    reverse = await hasn_contacts_dao.get_relation(db, owner_id, requester_id, 'social')
    if reverse and reverse.trust_level == 0:
        return response_base.fail(res=CustomResponse(code=400, msg='无法发送请求'))

    target_peer = _agent_peer_out(agent)

    # 已有待处理 agent 请求 → 幂等返回（Option A 重试 / daemon 兜底重发都安全，不报错）
    pending = await hasn_contact_requests_dao.get_active_pending(db, requester_id, agent_id, 'social')
    if pending:
        return response_base.success(
            data=HasnContactRequestOut(
                request_id=pending.id,
                status='pending',
                created_at=pending.created_time,
                channel_source=pending.channel_source,
                add_source=pending.add_source,
                target=target_peer,
                message=pending.message or '',
            ).model_dump()
        )

    # 信任等级与主人一致：取 请求方↔主人 social trust（默认 2）
    owner_relation = await hasn_contacts_dao.get_relation(db, requester_id, owner_id, 'social')
    trust_level = owner_relation.trust_level if owner_relation else 2

    req = await hasn_contact_requests_dao.create_request(
        db,
        from_id=requester_id,
        to_id=agent_id,
        to_owner_id=owner_id,
        to_type='agent',
        relation_type='social',
        requested_trust_level=trust_level,
        message=message,
        channel_source='manual',
        add_source=add_source,
    )
    await db.commit()

    requester = await hasn_humans_dao.get_by_hasn_id(db, requester_id)
    from_peer = HasnContactPeerOut(
        hasn_id=requester_id,
        star_id=getattr(requester, 'star_id', '') or '',
        name=_peer_display_name(requester, peer_type='human') if requester else '',
        type='human',
    )
    await _push_contact_event(
        owner_id,
        {
            'method': 'hasn.contact.request_received',
            'params': {
                'owner_id': owner_id,
                'request_id': req.id,
                'from_peer': from_peer.model_dump(),
                'target': target_peer.model_dump(),
                'message': msg_text,
            },
        },
    )
    return response_base.success(
        data=HasnContactRequestOut(
            request_id=req.id,
            status='pending',
            created_at=req.created_time,
            channel_source=req.channel_source,
            add_source=req.add_source,
            target=target_peer,
            message=msg_text,
        ).model_dump()
    )


@router.post('/request', summary='发送好友请求')
async def send_contact_request(
    obj_in: HasnContactRequestReq,
    db: CurrentSession,
    auth: Annotated[dict, Depends(hasn_auth)],
) -> ResponseModel:
    """发送好友请求 (social 关系)。

    请求落独立的 hasn_contact_requests 表，通过后才在 hasn_contacts 建边（见 ADR 2026-05-30）。
    两类目标：
    - human 唤星号 → 加好友（owner 级，加人）；目标即审批人本人。
    - agent 唤星号 → 请求把好友的『分身』加为联系人（agent 级）；审批人=分身主人，
      不再坍缩成主人、也不因主人已是好友而拦截（详见 _send_agent_contact_request）。
    校验：无 connected 关系 + 无 pending 请求 + 未被对方拉黑。
    """
    hasn_id = auth.get('effective_id', auth['hasn_id'])

    # 解析目标
    target, target_type = await _resolve_star_id(db, obj_in.target_star_id)
    if not target:
        return response_base.fail(res=CustomResponse(code=400, msg=f'唤星号 {obj_in.target_star_id} 不存在'))

    # agent 目标走分身级请求/审批闭环（审批人=分身主人）。
    if target_type == 'agent':
        return await _send_agent_contact_request(
            db, requester_id=hasn_id, agent=target, message=obj_in.message, add_source=obj_in.add_source
        )

    # human 目标：目标即审批人本人。
    to_id = target.hasn_id
    to_owner_id = target.hasn_id
    target_peer = HasnContactPeerOut(
        hasn_id=target.hasn_id,
        star_id=target.star_id,
        name=_peer_display_name(target, peer_type='human'),
        type='human',
    )

    if to_id == hasn_id:
        return response_base.fail(res=CustomResponse(code=400, msg='不能添加自己为好友'))

    # 校验 1：已是好友（connected）
    existing = await hasn_contacts_dao.get_relation(db, hasn_id, to_id, 'social')
    if existing and existing.status == 'connected':
        return response_base.fail(res=CustomResponse(code=400, msg='你们已经是好友'))

    # 校验 2：是否被对方拉黑（对方 → 我 方向 trust_level=0）
    reverse = await hasn_contacts_dao.get_relation(db, to_id, hasn_id, 'social')
    if reverse and reverse.trust_level == 0:
        return response_base.fail(res=CustomResponse(code=400, msg='无法向对方发送好友请求'))

    # 校验 3：已有待处理请求（部分唯一索引兜底，应用层先行拦截给友好提示）
    pending = await hasn_contact_requests_dao.get_active_pending(db, hasn_id, to_id, 'social')
    if pending:
        return response_base.fail(res=CustomResponse(code=400, msg='已有待处理的好友请求'))

    # 创建 pending 请求（不再在 hasn_contacts 建行）
    req = await hasn_contact_requests_dao.create_request(
        db,
        from_id=hasn_id,
        to_id=to_id,
        to_owner_id=to_owner_id,
        relation_type='social',
        requested_trust_level=2,
        message=obj_in.message,
        channel_source='manual',
        add_source=obj_in.add_source,
    )
    await db.commit()

    sender = await hasn_humans_dao.get_by_hasn_id(db, hasn_id)
    sender_peer = HasnContactPeerOut(
        hasn_id=hasn_id,
        star_id=getattr(sender, 'star_id', ''),
        name=_peer_display_name(sender, peer_type='human') if sender else '',
        type='human',
    )
    await _push_contact_event(
        to_owner_id,
        {
            'method': 'hasn.contact.request_received',
            'params': {
                'owner_id': to_owner_id,
                'request_id': req.id,
                'from_peer': sender_peer.model_dump(),
                'target': target_peer.model_dump(),
                'message': obj_in.message,
            },
        },
    )

    return response_base.success(
        data=HasnContactRequestOut(
            request_id=req.id,
            status='pending',
            created_at=req.created_time,
            channel_source=req.channel_source,
            add_source=req.add_source,
            target=target_peer,
            message=obj_in.message,
        ).model_dump()
    )


@router.get('/requests', summary='获取待处理好友请求')
async def list_pending_requests(
    db: CurrentSession,
    auth: Annotated[dict, Depends(hasn_auth)],
    direction: Annotated[str, Query(description='received=收到的, sent=自己发出的')] = 'received',
) -> ResponseModel:
    """获取待处理好友请求列表。

    - direction=received (默认): 我收到的待处理请求, 每条带 from_peer (发起方)
    - direction=sent: 我已发出但对方还没处理的请求, 每条带 target (目标方)
    """
    if direction not in ('received', 'sent'):
        raise HTTPException(status_code=422, detail='direction 必须是 received 或 sent')

    hasn_id = auth.get('effective_id', auth['hasn_id'])

    if direction == 'received':
        requests = await hasn_contact_requests_dao.get_received_pending(db, hasn_id)
        items = []
        for req in requests:
            sender = await hasn_humans_dao.get_by_hasn_id(db, req.from_id)
            if sender:
                from_peer = HasnContactPeerOut(
                    hasn_id=sender.hasn_id,
                    star_id=sender.star_id,
                    name=_peer_display_name(sender, peer_type='human'),
                    type='human',
                )
            else:
                # from_id 解析失败用 stub 占位, 不抛 500 (INV-15)
                from_peer = HasnContactPeerOut(
                    hasn_id=req.from_id,
                    star_id='',
                    name='',
                    type='human',
                )
            # agent 目标的请求：审批方收件箱要能渲染「请求联系的 AI分身」。
            target = None
            if req.to_type == 'agent':
                agent = await hasn_agents_dao.get_by_hasn_id(db, req.to_id)
                target = (
                    _agent_peer_out(agent)
                    if agent
                    else HasnContactPeerOut(hasn_id=req.to_id, star_id='', name='', type='agent')
                )
            items.append(
                HasnContactRequestOut(
                    request_id=req.id,
                    status=req.status,
                    created_at=req.created_time,
                    channel_source=req.channel_source,
                    add_source=req.add_source,
                    from_peer=from_peer,
                    target=target,
                    message=req.message or '',
                )
            )
        return response_base.success(data=[i.model_dump() for i in items])

    # direction == 'sent'：target 可能是 human，也可能是好友的『分身』(agent)
    requests = await hasn_contact_requests_dao.get_sent_pending(db, hasn_id)
    items = []
    for req in requests:
        if req.to_type == 'agent':
            agent = await hasn_agents_dao.get_by_hasn_id(db, req.to_id)
            target = (
                _agent_peer_out(agent)
                if agent
                else HasnContactPeerOut(hasn_id=req.to_id, star_id='', name='', type='agent')
            )
        else:
            target_human = await hasn_humans_dao.get_by_hasn_id(db, req.to_id)
            if target_human:
                target = HasnContactPeerOut(
                    hasn_id=target_human.hasn_id,
                    star_id=target_human.star_id,
                    name=_peer_display_name(target_human, peer_type='human'),
                    type='human',
                )
            else:
                target = HasnContactPeerOut(
                    hasn_id=req.to_id,
                    star_id='',
                    name='',
                    type='human',
                )
        items.append(
            HasnContactRequestOut(
                request_id=req.id,
                status=req.status,
                created_at=req.created_time,
                channel_source=req.channel_source,
                add_source=req.add_source,
                target=target,
                message=req.message or '',
            )
        )
    return response_base.success(data=[i.model_dump() for i in items])


@router.put('/requests/{request_id}/respond', summary='回应好友请求')
async def respond_to_request(
    request_id: int,
    obj_in: HasnContactRespondReq,
    db: CurrentSession,
    auth: Annotated[dict, Depends(hasn_auth)],
) -> ResponseModel:
    """回应好友请求：accept / reject（审批人）/ withdraw（发起方）。

    accept 时通过 UPSERT 在 hasn_contacts 建双向 connected 边（兜过历史 archived 行），
    并把请求标记 accepted、回填 resulting_contact_id（审计链）。
    """
    hasn_id = auth.get('effective_id', auth['hasn_id'])
    req = await hasn_contact_requests_dao.get(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail='好友请求不存在')
    if req.status != 'pending':
        return response_base.fail(res=CustomResponse(code=400, msg=f'该请求已处理 (status={req.status})'))

    trust = req.requested_trust_level or 2

    if obj_in.action == 'accept':
        if req.to_owner_id != hasn_id:
            raise HTTPException(status_code=403, detail='只有被请求方可以接受该请求')

        # agent 目标：只建『请求方 → 分身』单向 agent 边（分身回复依赖主人↔主人 trust，已≥2，
        # 无需反向 agent 边）。信任等级沿用请求时落库的『与主人一致』值。
        if req.to_type == 'agent':
            forward = await hasn_contacts_dao.upsert_connected(
                db, owner_id=req.from_id, peer_id=req.to_id, peer_type='agent',
                relation_type=req.relation_type, trust_level=trust,
                peer_owner_id=req.to_owner_id, channel_source=req.channel_source or 'manual',
                add_source=req.add_source, request_message=req.message,
            )
            await hasn_contact_requests_dao.mark_accepted(
                db, request_id, decided_by=hasn_id, resulting_contact_id=forward.id,
            )
            await db.commit()

            agent = await hasn_agents_dao.get_by_hasn_id(db, req.to_id)
            peer = (
                _agent_peer_out(agent)
                if agent
                else HasnContactPeerOut(hasn_id=req.to_id, star_id='', name='', type='agent')
            )
            await _push_contact_event(
                req.from_id,
                {
                    'method': 'hasn.contact.connected',
                    'params': {
                        'owner_id': req.from_id,
                        'request_id': request_id,
                        'peer': peer.model_dump(),
                        'trust_level': trust,
                    },
                },
            )
            return response_base.success(data={'status': 'connected', 'trust_level': trust})

        # UPSERT 双向边：发起方→目标、目标→发起方，均 connected
        forward = await hasn_contacts_dao.upsert_connected(
            db, owner_id=req.from_id, peer_id=req.to_id, peer_type='human',
            relation_type=req.relation_type, trust_level=trust,
            peer_owner_id=req.to_id, channel_source=req.channel_source or 'manual',
            add_source=req.add_source, request_message=req.message,
        )
        await hasn_contacts_dao.upsert_connected(
            db, owner_id=req.to_id, peer_id=req.from_id, peer_type='human',
            relation_type=req.relation_type, trust_level=trust,
            peer_owner_id=req.from_id, channel_source=req.channel_source or 'manual',
            request_message=req.message,
        )
        await hasn_contact_requests_dao.mark_accepted(
            db, request_id, decided_by=hasn_id, resulting_contact_id=forward.id,
        )
        await db.commit()

        acceptor = await hasn_humans_dao.get_by_hasn_id(db, req.to_id)
        peer = HasnContactPeerOut(
            hasn_id=req.to_id,
            star_id=getattr(acceptor, 'star_id', ''),
            name=_peer_display_name(acceptor, peer_type='human') if acceptor else '',
            type='human',
        )
        await _push_contact_event(
            req.from_id,
            {
                'method': 'hasn.contact.connected',
                'params': {
                    'owner_id': req.from_id,
                    'request_id': request_id,
                    'peer': peer.model_dump(),
                    'trust_level': trust,
                },
            },
        )
        return response_base.success(data={'status': 'connected', 'trust_level': trust})

    if obj_in.action == 'reject':
        if req.to_owner_id != hasn_id:
            raise HTTPException(status_code=403, detail='只有被请求方可以拒绝该请求')
        await hasn_contact_requests_dao.mark_rejected(db, request_id, decided_by=hasn_id)
        await db.commit()
        return response_base.success(data={'status': 'rejected'})

    if obj_in.action == 'withdraw':
        if req.from_id != hasn_id:
            raise HTTPException(status_code=403, detail='只有发起方可以撤回该请求')
        await hasn_contact_requests_dao.mark_withdrawn(db, request_id, decided_by=hasn_id)
        await db.commit()
        return response_base.success(data={'status': 'withdrawn'})

    return response_base.fail(res=CustomResponse(code=400, msg='action 必须是 accept / reject / withdraw'))


@router.get('', summary='联系人列表')
async def list_contacts(
    db: CurrentSession,
    auth: Annotated[dict, Depends(hasn_auth)],
    relation_type: Annotated[str | None, Query(description='关系类型筛选；不传则返回全部联系人')] = None,
) -> ResponseModel:
    hasn_id = auth.get('effective_id', auth['hasn_id'])
    contacts = await hasn_contacts_dao.list_contacts(db, hasn_id, relation_type=relation_type)

    items = []
    for c in contacts:
        # 查 peer 信息（使用 hasn_id）
        peer_info = await hasn_humans_dao.get_by_hasn_id(db, c.peer_id)
        if not peer_info:
            peer_info = await hasn_agents_dao.get_by_hasn_id(db, c.peer_id)
        if not peer_info:
            continue
        if c.peer_type == 'agent':
            peer_owner_id = c.peer_owner_id or getattr(peer_info, 'owner_id', None)
            if peer_owner_id == hasn_id:
                continue

        # 阶段二: 查询 human 联系人名下的 Agent 列表（含实时在线状态）。
        # 与详情构造共用 HasnContactsService.fetch_owned_agents_with_status，
        # 列表/详情同一份 owned_agents 定义 + 同源 online_status（修复列表路径
        # 此前漏 JOIN 运行时上报、头像无在线状态点的根因）。
        owned_agents: list[AgentPeerOut] = []
        if c.peer_type == 'human':
            agent_dicts = await HasnContactsService.fetch_owned_agents_with_status(db, c.peer_id)
            owned_agents.extend(
                AgentPeerOut(
                    hasn_id=ag['hasn_id'],
                    star_id=ag['star_id'],
                    name=ag['name'],
                    agent_name=ag['agent_name'],
                    avatar=ag.get('avatar'),
                    type=ag.get('type') or 'desktop',
                    role=ag.get('role') or 'specialist',
                    description=ag.get('description'),
                    bio=ag.get('bio'),
                    online_status=ag.get('online_status') or 'offline',
                    last_seen_at=ag.get('last_seen_at'),
                )
                for ag in agent_dicts
            )

        # HasnHumans 使用 nickname，HasnAgents 使用 display_name
        peer_name = peer_info.nickname if c.peer_type == 'human' else peer_info.display_name
        peer_user = await _resolve_peer_user_profile(db, peer_info, peer_type=c.peer_type)
        items.append(
            HasnContactOut(
                id=c.id,
                peer=HasnContactPeerOut(
                    hasn_id=peer_info.hasn_id,
                    star_id=peer_info.star_id,
                    name=peer_name,
                    type=c.peer_type,
                    avatar=getattr(peer_info, 'avatar', None),
                ),
                relation_type=c.relation_type,
                trust_level=c.trust_level,
                trust_level_label=TRUST_LEVEL_LABELS.get(c.trust_level, ''),
                channel_source=c.channel_source,
                add_source=c.add_source,
                nickname=c.nickname,
                bio=getattr(peer_user, 'bio', None),
                gender=getattr(peer_user, 'gender', None),
                province=getattr(peer_user, 'province', None),
                city=getattr(peer_user, 'city', None),
                district=getattr(peer_user, 'district', None),
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
            )
        )

    return response_base.success(data=HasnContactListResp(total=len(items), items=items).model_dump())


# ─── 阶段二: 权限矩阵 API ───────────────────────────────


@router.put('/{contact_id}/trust-level', summary='修改信任等级')
async def update_trust_level(
    contact_id: int,
    obj_in: HasnTrustLevelReq,
    db: CurrentSession,
    auth: Annotated[dict, Depends(hasn_auth)],
) -> ResponseModel:
    """
    修改联系人信任等级 (0-5)。
    铁律校验: trust_level=5 仅限自己的 Agent (peer_type='agent')
    """
    hasn_id = auth.get('effective_id', auth['hasn_id'])
    contact = await hasn_contacts_dao.get(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail='联系人不存在')
    if contact.owner_id != hasn_id:
        raise HTTPException(status_code=403, detail='无权修改此联系人')

    # 协议级约束 (Core/02 §7.4.1, Core/04 §1.4)
    # - 非 social 关系不得设置 trust_level=5（Owner 仅 social）
    # - service 关系不存在 Stranger 状态（trust_level=1）
    try:
        validate_relation_constraints(contact.relation_type, obj_in.trust_level)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={'code': ERR_TRUST_LEVEL_INVALID, 'msg': str(e)},
        ) from e

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

    return response_base.success(
        data={
            'contact_id': contact_id,
            'trust_level': obj_in.trust_level,
            'trust_level_label': TRUST_LEVEL_LABELS.get(obj_in.trust_level, ''),
        }
    )


@router.put('/{contact_id}/permissions', summary='自定义权限覆盖')
async def update_permissions(
    contact_id: int,
    obj_in: HasnPermissionsReq,
    db: CurrentSession,
    auth: Annotated[dict, Depends(hasn_auth)],
) -> ResponseModel:
    """
    覆盖特定联系人的权限（叠加在默认矩阵之上）。
    系统会对所有覆盖项进行铁律冲突校验，违反任一铁律则拒绝整个请求。
    """
    hasn_id = auth.get('effective_id', auth['hasn_id'])
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

    return response_base.success(
        data={
            'contact_id': contact_id,
            'custom_permissions': contact.custom_permissions,
        }
    )


@router.get('/{contact_id}/effective-permissions', summary='有效权限')
async def get_effective_permissions(
    contact_id: int,
    db: CurrentSession,
    auth: Annotated[dict, Depends(hasn_auth)],
) -> ResponseModel:
    """
    返回合并后的有效权限（默认矩阵 + custom_permissions 覆盖）。
    可用于前端在发起行为前检查权限状态。
    """
    hasn_id = auth.get('effective_id', auth['hasn_id'])
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

    return response_base.success(
        data={
            'contact_id': contact_id,
            'relation_type': contact.relation_type,
            'trust_level': contact.trust_level,
            'trust_level_label': TRUST_LEVEL_LABELS.get(contact.trust_level, ''),
            'effective_permissions': effective,
        }
    )
