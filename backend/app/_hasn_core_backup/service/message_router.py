"""HASN 消息路由核心服务

实现消息路由全流程（对齐协议 02-消息与通信.md §3.1）：
认证 → 目标解析 → 关系查询 → 权限检查 → 铁律检查 → 持久化 → 投递
"""

import uuid
from typing import Any

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.db import async_db_session
from backend.utils.timezone import timezone

from backend.app.hasn_core.model import HasnHumans, HasnMessages, HasnConversations, HasnUnreadCounts
from backend.app.hasn_core.model.hasn_agents import HasnAgents
from backend.app.hasn_core.model.hasn_contacts import HasnContact
from backend.app.hasn_core.service.ws_router import ws_router


# ─── 目标解析 ───

async def resolve_target(db: AsyncSession, target: str) -> dict[str, Any] | None:
    """
    解析目标地址（Star ID 或 HASN ID）→ 实体信息

    返回: {hasn_id, star_id, entity_type, name} 或 None
    """
    # 直接是 HASN ID
    if target.startswith('h_'):
        result = await db.execute(
            select(HasnHumans).where(HasnHumans.hasn_id == target)
        )
        human = result.scalar_one_or_none()
        if human:
            return {
                'hasn_id': human.hasn_id,
                'star_id': human.star_id,
                'entity_type': 'human',
                'name': human.name,
            }
        return None

    if target.startswith('a_'):
        result = await db.execute(
            select(HasnAgents).where(HasnAgents.hasn_id == target)
        )
        agent = result.scalar_one_or_none()
        if agent:
            return {
                'hasn_id': agent.hasn_id,
                'star_id': agent.star_id,
                'entity_type': 'agent',
                'name': agent.name,
                'owner_id': agent.owner_id,
            }
        return None

    # Star ID 解析
    if '#' in target:
        # Agent Star ID: 100001#star
        result = await db.execute(
            select(HasnAgents).where(HasnAgents.star_id == target)
        )
        agent = result.scalar_one_or_none()
        if agent:
            return {
                'hasn_id': agent.hasn_id,
                'star_id': agent.star_id,
                'entity_type': 'agent',
                'name': agent.name,
                'owner_id': agent.owner_id,
            }
    else:
        # Human Star ID: 100001 或 fuzi
        result = await db.execute(
            select(HasnHumans).where(HasnHumans.star_id == target)
        )
        human = result.scalar_one_or_none()
        if human:
            return {
                'hasn_id': human.hasn_id,
                'star_id': human.star_id,
                'entity_type': 'human',
                'name': human.name,
            }

    return None


# ─── 关系与权限检查 ───

async def check_relation_permission(
    db: AsyncSession,
    sender_id: str,
    receiver_id: str,
    msg_type: str = 'message',
) -> dict[str, Any]:
    """
    检查发送方与接收方之间的关系和权限

    返回: {allowed: bool, relation_type, trust_level, reason}
    """
    # 自己给自己发（用户给自己的 Agent）→ 始终允许
    if sender_id == receiver_id:
        return {'allowed': True, 'relation_type': 'social', 'trust_level': 5}

    # 检查是否是 Owner 给自己的 Agent 发消息
    if sender_id.startswith('h_') and receiver_id.startswith('a_'):
        agent_result = await db.execute(
            select(HasnAgents).where(
                HasnAgents.hasn_id == receiver_id,
                HasnAgents.owner_id == sender_id,
            )
        )
        if agent_result.scalar_one_or_none():
            return {'allowed': True, 'relation_type': 'social', 'trust_level': 5}

    # Agent 给自己的 Owner 发消息 → 始终允许
    if sender_id.startswith('a_') and receiver_id.startswith('h_'):
        agent_result = await db.execute(
            select(HasnAgents).where(
                HasnAgents.hasn_id == sender_id,
                HasnAgents.owner_id == receiver_id,
            )
        )
        if agent_result.scalar_one_or_none():
            return {'allowed': True, 'relation_type': 'social', 'trust_level': 5}

    # 同一 Owner 的 Agent 之间 → 始终允许
    if sender_id.startswith('a_') and receiver_id.startswith('a_'):
        sender_agent = await db.execute(
            select(HasnAgents.owner_id).where(HasnAgents.hasn_id == sender_id)
        )
        receiver_agent = await db.execute(
            select(HasnAgents.owner_id).where(HasnAgents.hasn_id == receiver_id)
        )
        s_owner = sender_agent.scalar()
        r_owner = receiver_agent.scalar()
        if s_owner and r_owner and s_owner == r_owner:
            return {'allowed': True, 'relation_type': 'social', 'trust_level': 5}

    # 查询关系记录（双向查找，取发送方视角）
    # 对于 Agent，用其 Owner 的身份查关系
    sender_lookup = sender_id
    receiver_lookup = receiver_id

    if sender_id.startswith('a_'):
        result = await db.execute(
            select(HasnAgents.owner_id).where(HasnAgents.hasn_id == sender_id)
        )
        owner = result.scalar()
        if owner:
            sender_lookup = owner

    if receiver_id.startswith('a_'):
        result = await db.execute(
            select(HasnAgents.owner_id).where(HasnAgents.hasn_id == receiver_id)
        )
        owner = result.scalar()
        if owner:
            receiver_lookup = owner

    # 查询关系
    relation_result = await db.execute(
        select(HasnContact).where(
            HasnContact.owner_id == sender_lookup,
            HasnContact.peer_id == receiver_lookup,
            HasnContact.status == 'connected',
        )
    )
    relation = relation_result.scalar_one_or_none()

    if not relation:
        # 好友请求类消息不需要已有关系
        if msg_type in ('contact_request', 'contact_accept', 'contact_reject'):
            return {'allowed': True, 'relation_type': 'social', 'trust_level': 1}
        return {
            'allowed': False,
            'relation_type': None,
            'trust_level': 0,
            'reason': '双方无关系，请先添加好友',
        }

    # 检查是否被拉黑
    if relation.trust_level == 0:
        return {
            'allowed': False,
            'relation_type': relation.relation_type,
            'trust_level': 0,
            'reason': '已被对方拉黑',
        }

    # 基本权限：trust_level >= 2 可发消息
    if relation.trust_level >= 2:
        return {
            'allowed': True,
            'relation_type': relation.relation_type,
            'trust_level': relation.trust_level,
        }

    # Stranger (trust_level=1) 只能发特定类型消息
    if relation.trust_level == 1:
        if msg_type in ('contact_request', 'discovery_query'):
            return {
                'allowed': True,
                'relation_type': relation.relation_type,
                'trust_level': 1,
            }
        return {
            'allowed': False,
            'relation_type': relation.relation_type,
            'trust_level': 1,
            'reason': '信任等级不足，仅允许好友请求',
        }

    return {
        'allowed': False,
        'relation_type': relation.relation_type,
        'trust_level': relation.trust_level,
        'reason': '权限不足',
    }


# ─── 会话管理 ───

async def get_or_create_conversation(
    db: AsyncSession,
    participant_a_id: str,
    participant_a_type: str,
    participant_b_id: str,
    participant_b_type: str,
    relation_type: str = 'social',
) -> HasnConversations:
    """获取或创建单聊会话（约定 a < b 字典序保证唯一性）"""
    # 排序保证唯一性
    if participant_a_id > participant_b_id:
        participant_a_id, participant_b_id = participant_b_id, participant_a_id
        participant_a_type, participant_b_type = participant_b_type, participant_a_type

    # 查找已有会话
    result = await db.execute(
        select(HasnConversations).where(
            HasnConversations.type == 'direct',
            HasnConversations.participant_a_id == participant_a_id,
            HasnConversations.participant_b_id == participant_b_id,
            HasnConversations.relation_type == relation_type,
        )
    )
    conv = result.scalar_one_or_none()

    if conv:
        return conv

    # 创建新会话
    conv = HasnConversations(
        type='direct',
        relation_type=relation_type,
        participant_a_id=participant_a_id,
        participant_b_id=participant_b_id,
        participant_a_type=participant_a_type,
        participant_b_type=participant_b_type,
    )
    db.add(conv)
    await db.flush()
    return conv


# ─── 消息持久化 ───

def _entity_type_int(hasn_id: str) -> int:
    """hasn_id → from_type/to_type 数字"""
    if hasn_id.startswith('h_'):
        return 1  # human
    elif hasn_id.startswith('a_'):
        return 2  # agent
    return 3  # system


async def persist_message(
    db: AsyncSession,
    conversation_id: str,
    from_id: str,
    to_id: str,
    content: dict,
    content_type: int = 1,
    msg_type: str = 'message',
    priority: str = 'normal',
    reply_to_id: int | None = None,
    local_id: str | None = None,
    context: dict | None = None,
) -> HasnMessages:
    """持久化消息并更新会话"""
    now = timezone.now()

    msg = HasnMessages(
        conversation_id=conversation_id,
        from_id=from_id,
        from_type=_entity_type_int(from_id),
        to_id=to_id,
        to_type=_entity_type_int(to_id),
        content_type=content_type,
        content=content,
        msg_type=msg_type,
        status=1,  # sent
        priority=priority,
        reply_to_id=reply_to_id,
        local_id=local_id,
        context=context,
        server_received_at=now,
    )
    db.add(msg)
    await db.flush()

    # 更新会话最后消息
    conv = await db.get(HasnConversations, conversation_id)
    if conv:
        conv.last_message_id = msg.id
        conv.last_message_at = now
        conv.last_message_from = from_id
        conv.message_count = (conv.message_count or 0) + 1
        # 生成预览
        if content_type == 1:  # 文本
            text = content.get('text', '')
            conv.last_message_preview = text[:200] if text else ''
        elif content_type == 2:
            conv.last_message_preview = '[图片]'
        elif content_type == 3:
            conv.last_message_preview = '[文件]'
        elif content_type == 4:
            conv.last_message_preview = '[语音]'
        elif content_type == 5:
            conv.last_message_preview = '[卡片]'
        else:
            conv.last_message_preview = '[消息]'

    # 更新接收方未读计数
    unread_result = await db.execute(
        select(HasnUnreadCounts).where(
            HasnUnreadCounts.hasn_id == to_id,
            HasnUnreadCounts.conversation_id == conversation_id,
        )
    )
    unread = unread_result.scalar_one_or_none()
    if unread:
        unread.unread_count = (unread.unread_count or 0) + 1
    else:
        unread = HasnUnreadCounts(
            hasn_id=to_id,
            conversation_id=conversation_id,
            unread_count=1,
            last_read_msg_id=0,
        )
        db.add(unread)

    await db.flush()
    return msg


# ─── 消息路由主入口 ───

async def route_message(
    db: AsyncSession,
    from_id: str,
    to_target: str,
    content: dict,
    content_type: int = 1,
    msg_type: str = 'message',
    priority: str = 'normal',
    reply_to_id: int | None = None,
    local_id: str | None = None,
    context: dict | None = None,
) -> dict[str, Any]:
    """
    消息路由主入口

    流程：目标解析 → 关系检查 → 权限检查 → 获取/创建会话 → 持久化 → 投递

    返回: {msg_id, conversation_id, status, local_id}
    """
    # 1. 目标解析
    target_info = await resolve_target(db, to_target)
    if not target_info:
        return {'error': True, 'code': 3001, 'message': f'目标 {to_target} 不存在'}

    to_id = target_info['hasn_id']
    to_type = target_info['entity_type']

    # 2. 不能给自己发消息（同一 hasn_id）
    if from_id == to_id:
        return {'error': True, 'code': 2006, 'message': '不能给自己发消息'}

    # 3. 关系与权限检查
    perm = await check_relation_permission(db, from_id, to_id, msg_type)
    if not perm['allowed']:
        return {
            'error': True,
            'code': 2002,
            'message': perm.get('reason', '权限不足'),
        }

    # 4. 获取/创建会话
    from_type = 'human' if from_id.startswith('h_') else 'agent'
    relation_type = perm.get('relation_type', 'social') or 'social'

    conv = await get_or_create_conversation(
        db, from_id, from_type, to_id, to_type, relation_type
    )

    # 5. 持久化
    msg = await persist_message(
        db=db,
        conversation_id=str(conv.id),
        from_id=from_id,
        to_id=to_id,
        content=content,
        content_type=content_type,
        msg_type=msg_type,
        priority=priority,
        reply_to_id=reply_to_id,
        local_id=local_id,
        context=context,
    )

    await db.commit()

    # 6. 构建推送 payload
    payload = {
        'cmd': 'MESSAGE',
        'to_id': to_id,
        'message': {
            'id': msg.id,
            'conversation_id': str(conv.id),
            'from_id': from_id,
            'from_type': msg.from_type,
            'to_id': to_id,
            'to_type': msg.to_type,
            'content_type': content_type,
            'content': content,
            'msg_type': msg_type,
            'status': 1,
            'priority': priority,
            'reply_to_id': reply_to_id,
            'local_id': local_id,
            'created_time': msg.created_time.isoformat() if msg.created_time else None,
        },
    }

    # 7. 投递
    await ws_router.push_message_to(to_id, payload)

    return {
        'error': False,
        'msg_id': msg.id,
        'conversation_id': str(conv.id),
        'status': 'sent',
        'local_id': local_id,
    }


# ─── 已读处理 ───

async def mark_read(
    db: AsyncSession,
    hasn_id: str,
    conversation_id: str,
    last_msg_id: int,
) -> None:
    """标记会话已读"""
    result = await db.execute(
        select(HasnUnreadCounts).where(
            HasnUnreadCounts.hasn_id == hasn_id,
            HasnUnreadCounts.conversation_id == conversation_id,
        )
    )
    unread = result.scalar_one_or_none()

    if unread:
        unread.unread_count = 0
        unread.last_read_msg_id = last_msg_id
    else:
        unread = HasnUnreadCounts(
            hasn_id=hasn_id,
            conversation_id=conversation_id,
            unread_count=0,
            last_read_msg_id=last_msg_id,
        )
        db.add(unread)

    await db.commit()


# ─── 消息撤回 ───

async def recall_message(
    db: AsyncSession,
    hasn_id: str,
    msg_id: int,
) -> dict[str, Any]:
    """撤回消息"""
    result = await db.execute(
        select(HasnMessages).where(HasnMessages.id == msg_id)
    )
    msg = result.scalar_one_or_none()

    if not msg:
        return {'error': True, 'code': 3001, 'message': '消息不存在'}

    # 只能撤回自己发的消息，或 Owner 撤回 Agent 的消息
    can_recall = False
    if msg.from_id == hasn_id:
        can_recall = True
    elif hasn_id.startswith('h_') and msg.from_id.startswith('a_'):
        agent_result = await db.execute(
            select(HasnAgents).where(
                HasnAgents.hasn_id == msg.from_id,
                HasnAgents.owner_id == hasn_id,
            )
        )
        if agent_result.scalar_one_or_none():
            can_recall = True

    if not can_recall:
        return {'error': True, 'code': 2002, 'message': '无权撤回此消息'}

    if msg.status == 4:  # 已撤回
        return {'error': True, 'code': 3014, 'message': '消息已被撤回'}

    # 执行撤回
    msg.status = 4  # recalled
    msg.recalled_at = timezone.now()
    msg.recalled_by = hasn_id
    await db.commit()

    # 通知对方
    recall_payload = {
        'cmd': 'MESSAGE_RECALLED',
        'msg_id': msg_id,
        'conversation_id': str(msg.conversation_id),
        'recalled_by': hasn_id,
    }
    await ws_router.push_message_to(msg.to_id, recall_payload)

    return {'error': False, 'msg_id': msg_id}
