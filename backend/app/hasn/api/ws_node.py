"""HASN 统一节点 WebSocket 端点.

现行控制平面：
- add_owner / remove_owner / renew_owner / list_owners
- add_agent / remove_agent
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.security.utils import get_authorization_scheme_param

from backend.database.db import async_db_session
from backend.app.hasn.service.hasn_auth import verify_node_key
from backend.app.hasn.service.ws_router import ws_router, _ws_connections
from backend.app.hasn.service import message_router
from backend.utils.timezone import timezone

log = logging.getLogger(__name__)

router = APIRouter()

# 协议版本
HASN_PROTOCOL = 'hasn/2.0'


def _frame(method: str, params: dict) -> dict:
    """构造标准 HASN 事件帧"""
    return {
        'hasn': HASN_PROTOCOL,
        'method': method,
        'params': params,
    }


def _response(req_id: str, result: dict = None, error: dict = None) -> dict:
    """构造标准 HASN 响应帧"""
    resp = {'hasn': HASN_PROTOCOL, 'id': req_id}
    if error:
        resp['error'] = error
    else:
        resp['result'] = result or {}
    return resp


@router.websocket('/ws/node')
async def hasn_node_websocket(
    websocket: WebSocket,
):
    """HASN 统一节点 WebSocket 端点（所有节点类型共用）"""

    # 1. 认证：只接受 Authorization: NodeKey <hasn_nk_xxx>
    try:
        authorization = websocket.headers.get('Authorization')
        if not authorization:
            await websocket.close(code=4001, reason='缺少认证头 Authorization')
            return
        scheme, credentials = get_authorization_scheme_param(authorization)
        if scheme != 'NodeKey':
            await websocket.close(code=4001, reason='仅支持 NodeKey 认证')
            return
        auth = await verify_node_key(credentials)
    except Exception as e:
        await websocket.close(code=4001, reason=str(e))
        return

    node_id = auth.get('node_id') or auth.get('client_id', '')
    node_type = auth.get('node_type') or auth.get('client_type', 'desktop')
    capacity = auth.get('capacity', 1)

    await websocket.accept()

    # 2. 注册节点在线（不绑定用户）
    await ws_router.register_node(
        node_id, node_type, websocket, capacity
    )

    try:
        # 3. 发送 hasn.connected
        await websocket.send_json(_frame('hasn.connected', {
            'node_id': node_id,
            'node_type': node_type,
            'capacity': capacity,
            'server_time': timezone.now().isoformat(),
            'supported_versions': ['hasn/2.0'],
            'extensions': [
                'capability', 'discovery', 'trade',
                'screening', 'health', 'constellation', 'bridge',
            ],
        }))

        # 4. 双向收发循环
        await _recv_loop(websocket, node_id)

    except WebSocketDisconnect:
        log.info(f'节点断开: {node_id} (type={node_type})')
    except Exception as e:
        log.error(f'WebSocket 异常: {node_id} - {e}')
    finally:
        # 5. 清理：注销节点 + 清理所有实体
        await ws_router.unregister_node(node_id)

async def _recv_loop(
    websocket: WebSocket,
    node_id: str,
) -> None:
    """处理节点上行消息"""
    # 记录当前 node 的活跃主体（bound owners + online agents），用于 from_id 校验
    active_entities: set[str] = set()

    while True:
        raw = await websocket.receive_text()
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            await _send_error(websocket, 2004, 'JSON 格式错误')
            continue

        method = msg.get('method', '')
        params = msg.get('params', {})
        req_id = msg.get('id')

        try:
            if method == 'hasn.node.add_owner':
                await _handle_add_owner(websocket, node_id, params, active_entities)

            elif method == 'hasn.node.remove_owner':
                await _handle_remove_owner(websocket, node_id, params, active_entities)

            elif method == 'hasn.node.renew_owner':
                await _handle_renew_owner(websocket, node_id, params, active_entities)

            elif method == 'hasn.node.list_owners':
                await _handle_list_owners(websocket, node_id)

            elif method == 'hasn.node.add_agent':
                await _handle_add_agent(websocket, node_id, params, active_entities)

            elif method == 'hasn.node.remove_agent':
                await _handle_remove_agent(websocket, node_id, params, active_entities)

            elif method == 'hasn.agent.register':
                await _handle_agent_register(
                    websocket, node_id, params, active_entities, req_id,
                )

            elif method == 'hasn.agent.deregister':
                await _handle_agent_deregister(
                    websocket, node_id, params, active_entities, req_id,
                )

            elif method == 'hasn.message.send':
                await _handle_send(
                    websocket, node_id, params, active_entities,
                )

            elif method == 'hasn.message.read':
                await _handle_read(params, active_entities)

            elif method == 'hasn.typing':
                await _handle_typing(params, active_entities)

            elif method == 'hasn.ping':
                await websocket.send_json(_frame('hasn.pong', {
                    'ts': params.get('ts'),
                }))

            else:
                await _send_error(websocket, 9001, f'未知方法: {method}')

        except Exception as e:
            log.error(f'处理命令 {method} 异常: {e}', exc_info=True)
            await _send_error(websocket, 9001, '服务器内部错误')


# ─── 命令处理器 ───


async def _handle_add_owner(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
) -> None:
    async with async_db_session() as db:
        result = await ws_router.add_owner(
            node_id=node_id,
            owner_id=params.get('owner_id', ''),
            owner_proof=params.get('owner_proof', {}),
            db=db,
        )
        await db.commit()
    owner_id = result.get('owner_id', '')
    if result.get('accepted') and owner_id:
        active_entities.add(owner_id)
        offline_msgs = await ws_router.get_offline_messages([owner_id])
        if offline_msgs:
            await websocket.send_json(_frame('hasn.node.offline_messages', {'messages': offline_msgs}))
    await websocket.send_json(_frame('hasn.node.add_owner_ack', result))


async def _handle_remove_owner(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
) -> None:
    owner_id = params.get('owner_id', '')
    async with async_db_session() as db:
        result = await ws_router.remove_owner(node_id=node_id, owner_id=owner_id, db=db)
        await db.commit()
    active_entities.discard(owner_id)
    await websocket.send_json(_frame('hasn.node.remove_owner_ack', result))


async def _handle_renew_owner(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
) -> None:
    async with async_db_session() as db:
        result = await ws_router.renew_owner(
            node_id=node_id,
            owner_id=params.get('owner_id', ''),
            owner_proof=params.get('owner_proof', {}),
            db=db,
        )
        await db.commit()
    await websocket.send_json(_frame('hasn.node.renew_owner_ack', result))


async def _handle_list_owners(websocket: WebSocket, node_id: str) -> None:
    async with async_db_session() as db:
        result = await ws_router.list_owners(node_id=node_id, db=db)
    await websocket.send_json(_frame('hasn.node.list_owners_ack', result))


async def _handle_add_agent(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
) -> None:
    async with async_db_session() as db:
        result = await ws_router.add_agent_presence(
            node_id=node_id,
            agent_id=params.get('agent_id', ''),
            owner_id=params.get('owner_id', ''),
            db=db,
        )
        await db.commit()
    agent_id = params.get('agent_id', '')
    if result.get('accepted') and agent_id:
        active_entities.add(agent_id)
        offline_msgs = await ws_router.get_offline_messages([agent_id])
        if offline_msgs:
            await websocket.send_json(_frame('hasn.node.offline_messages', {'messages': offline_msgs}))
    await websocket.send_json(_frame('hasn.node.add_agent_ack', result))


async def _handle_remove_agent(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
) -> None:
    agent_id = params.get('agent_id', '')
    result = await ws_router.remove_agent_presence(node_id=node_id, agent_id=agent_id)
    active_entities.discard(agent_id)
    await websocket.send_json(_frame('hasn.node.remove_agent_ack', result))


async def _handle_agent_register(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
    req_id: str | None,
) -> None:
    """处理 hasn.agent.register（通过 WS 创建新 Agent）"""
    from backend.app.hasn.service.hasn_auth import register_hasn_agent

    # 确定 owner_id：显式指定 or 从已上报的 Human 推断
    owner_id = params.get('owner_id', '')
    if not owner_id:
        humans = [eid for eid in active_entities if eid.startswith('h_')]
        if len(humans) == 1:
            owner_id = humans[0]
        elif len(humans) == 0:
            await _send_error(websocket, 8007, '未上报任何 Human 实体，无法确定 owner_id')
            return
        else:
            await _send_error(websocket, 8008, '多个 Human 实体在线，必须显式指定 owner_id')
            return

    agent_name = params.get('agent_name', '')
    display_name = params.get('display_name', '')

    if not agent_name or not display_name:
        await _send_error(websocket, 2002, '缺少必填参数 agent_name 或 display_name')
        return

    async with async_db_session() as db:
        try:
            result = await register_hasn_agent(
                db=db,
                owner_hasn_id=owner_id,
                agent_name=agent_name,
                display_name=display_name,
                agent_type=params.get('agent_type', 'local'),
                role=params.get('role', 'specialist'),
                description=params.get('description'),
                capabilities=params.get('capabilities'),
            )
            await db.commit()
        except Exception as e:
            await _send_error(websocket, 9001, f'Agent 注册失败: {e}')
            return

    ack_params = {
        'hasn_id': result['agent'].hasn_id,
        'star_id': result['agent'].star_id,
        'already_exists': result['already_exists'],
    }
    if result.get('agent_key'):
        ack_params['agent_key'] = result['agent_key']

    await websocket.send_json(_frame('hasn.agent.register_ack', ack_params))


async def _handle_agent_deregister(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
    req_id: str | None,
) -> None:
    """处理 hasn.agent.deregister（永久删除 Agent）"""
    hasn_id = params.get('hasn_id', '')
    if not hasn_id:
        await _send_error(websocket, 2002, '缺少 hasn_id')
        return

    # 先下线
    await ws_router.unregister_entity_route(node_id, hasn_id)
    active_entities.discard(hasn_id)

    # DB 标记删除
    from backend.app.hasn.model.hasn_agents import HasnAgents
    from sqlalchemy import update

    async with async_db_session() as db:
        await db.execute(
            update(HasnAgents)
            .where(HasnAgents.hasn_id == hasn_id)
            .values(status='deleted')
        )
        await db.commit()

    await websocket.send_json(_frame('hasn.agent.deregister_ack', {
        'hasn_id': hasn_id,
        'success': True,
    }))


async def _handle_send(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    active_entities: set[str],
) -> None:
    """处理 hasn.message.send"""
    from_id = params.get('from_id', '')
    to_target = params.get('to', '')
    content = params.get('content', {})
    local_id = params.get('local_id')
    msg_type = params.get('type', 'message')
    reply_to_id = params.get('context', {}).get('reply_to')

    # 校验 from_id 合法性：必须是已上报的实体
    if from_id not in active_entities:
        await _send_error(websocket, 8006, f'未授权的 from_id: {from_id}（不在已上报实体中）')
        return

    if not to_target:
        await _send_error(websocket, 2002, '缺少目标地址 (to)')
        return

    # 处理 content 格式
    content_type = 1  # 默认文本
    if isinstance(content, str):
        content = {'text': content}
    elif isinstance(content, dict):
        ct = content.get('content_type', 'text')
        if ct == 'text':
            content_type = 1
        elif ct == 'image':
            content_type = 2
        # 提取 body
        if 'body' in content:
            content = content['body']

    # 路由消息
    async with async_db_session() as db:
        result = await message_router.route_message(
            db=db,
            from_id=from_id,
            to_target=to_target,
            content=content,
            content_type=content_type,
            msg_type=msg_type,
            local_id=local_id,
            reply_to_id=reply_to_id,
        )

    if result.get('error'):
        await _send_error(websocket, result.get('code', 9001), result.get('message', ''))
        return

    # 发送 ACK
    await websocket.send_json(_frame('hasn.message.ack', {
        'msg_id': result['msg_id'],
        'conversation_id': result['conversation_id'],
        'local_id': local_id,
        'status': 'sent',
        'timestamp': timezone.now().isoformat(),
    }))

    # 多端同步：推送给发送方的其他节点
    from backend.database.redis import redis_client
    from backend.app.hasn.service.ws_router import USER_NODES_PREFIX

    # 找出 from_id 对应的 owner（如果是 Agent，找 owner 的其他节点）
    sync_target = from_id if from_id.startswith('h_') else None
    if not sync_target:
        # Agent 发送，找 owner 的节点
        for eid in active_entities:
            if eid.startswith('h_'):
                sync_target = eid
                break

    if sync_target:
        sender_payload = _frame('hasn.message.received', {
            'to_id': sync_target,
            'message': {
                'id': result['msg_id'],
                'conversation_id': result['conversation_id'],
                'from_id': from_id,
                'from_type': 1 if from_id.startswith('h_') else 2,
                'to_id': to_target,
                'to_type': 1 if to_target.startswith('h_') else 2,
                'content_type': content_type,
                'content': content,
                'msg_type': msg_type,
                'status': 1,
                'local_id': local_id,
                'self_sent': True,
                'created_time': timezone.now().isoformat(),
            },
        })
        other_nodes = await redis_client.smembers(f'{USER_NODES_PREFIX}:{sync_target}')
        for nid in other_nodes:
            if nid != node_id:
                other_ws = _ws_connections.get(nid)
                if other_ws:
                    try:
                        await other_ws.send_json(sender_payload)
                    except Exception:
                        pass


async def _handle_read(params: dict, active_entities: set[str]) -> None:
    """处理 hasn.message.read"""
    conversation_id = params.get('conversation_id', '')
    last_msg_id = params.get('last_msg_id', 0)

    if not conversation_id:
        return

    # 用已上报实体中的第一个 Human 作为 reader
    reader = next((eid for eid in active_entities if eid.startswith('h_')), '')
    if not reader:
        return

    async with async_db_session() as db:
        await message_router.mark_read(db, reader, conversation_id, last_msg_id)


async def _handle_typing(params: dict, active_entities: set[str]) -> None:
    """处理 hasn.typing"""
    to_id = params.get('to_id', '')
    conversation_id = params.get('conversation_id', '')

    if not to_id:
        return

    # 用已上报的第一个 Human 作为 from_id
    from_id = params.get('from_id', '')
    if not from_id:
        from_id = next((eid for eid in active_entities if eid.startswith('h_')), '')

    typing_payload = _frame('hasn.typing', {
        'from_id': from_id,
        'conversation_id': conversation_id,
    })
    await ws_router.push_message_to(to_id, typing_payload)


async def _send_error(websocket: WebSocket, code: int, message: str) -> None:
    """发送错误帧"""
    await websocket.send_json(_frame('hasn.error', {
        'code': code,
        'message': message,
    }))
