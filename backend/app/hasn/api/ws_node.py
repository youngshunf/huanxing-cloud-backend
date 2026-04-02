"""HASN 统一节点 WebSocket 端点

统一节点架构 (v4.0)：
- 端点: /api/v1/hasn/ws/node?token=<jwt> 或 ?api_key=<hasn_ak_xxx>
- 所有节点类型（desktop/mobile/web/cloud）共用同一端点
- 上行: REPORT_AGENTS, ADD_AGENT, REMOVE_AGENT, SEND, READ, TYPING, PING
- 下行: CONNECTED, REPORT_AGENTS_ACK, ADD_AGENT_ACK, MESSAGE, OFFLINE_MESSAGES,
        ACK, TYPING, READ_RECEIPT, PROVISION_AGENT, DEPROVISION_AGENT, PONG, ERROR
"""

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from backend.database.db import async_db_session
from backend.app.hasn.service.hasn_auth import verify_client_jwt, verify_node_api_key
from backend.app.hasn.service.ws_router import ws_router, _ws_connections
from backend.app.hasn.service import message_router
from backend.utils.timezone import timezone

log = logging.getLogger(__name__)

router = APIRouter()


@router.websocket('/ws/node')
async def hasn_node_websocket(
    websocket: WebSocket,
    token: str = Query(None),
    api_key: str = Query(None),
):
    """HASN 统一节点 WebSocket 端点（所有节点类型共用）"""

    # 1. 认证：支持 JWT token 或 API Key 两种方式
    try:
        if api_key:
            auth = await verify_node_api_key(api_key)
        elif token:
            auth = verify_client_jwt(token)
        else:
            await websocket.close(code=4001, reason='缺少认证凭据 (token 或 api_key)')
            return
    except Exception as e:
        await websocket.close(code=4001, reason=str(e))
        return

    user_hasn_id = auth['sub']
    node_id = auth.get('node_id') or auth.get('client_id', '')
    node_type = auth.get('node_type') or auth.get('client_type', 'desktop')
    star_id = auth.get('star_id', '')
    capacity = auth.get('capacity', 1)

    await websocket.accept()

    # 2. 注册节点在线
    await ws_router.register_node(
        node_id, user_hasn_id, node_type, websocket, capacity
    )

    try:
        # 3. 发送 CONNECTED（统一节点握手）
        await websocket.send_json({
            'cmd': 'CONNECTED',
            'node_id': node_id,
            'node_type': node_type,
            'capacity': capacity,
            # 兼容旧客户端
            'user_hasn_id': user_hasn_id,
            'client_id': node_id,
            'star_id': star_id,
            'server_time': timezone.now().isoformat(),
        })

        # 4. 双向收发循环
        await _recv_loop(websocket, node_id, user_hasn_id)

    except WebSocketDisconnect:
        log.info(f'节点断开: {node_id} ({user_hasn_id}, type={node_type})')
    except Exception as e:
        log.error(f'WebSocket 异常: {node_id} - {e}')
    finally:
        # 5. 清理：注销节点 + 解绑所有 Agent
        await ws_router.unregister_node(node_id, user_hasn_id)


# ─── 兼容旧 /ws/client 端点 ───

@router.websocket('/ws/client')
async def hasn_client_websocket_compat(
    websocket: WebSocket,
    token: str = Query(...),
):
    """兼容旧 /ws/client 端点 → 内部转发到统一节点逻辑"""
    await hasn_node_websocket(websocket, token=token, api_key=None)


async def _recv_loop(
    websocket: WebSocket,
    node_id: str,
    user_hasn_id: str,
) -> None:
    """处理节点上行消息"""
    # 记录已上报的 Agent（用于 from_id 校验）
    reported_agents: set[str] = set()

    while True:
        raw = await websocket.receive_text()
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            await _send_error(websocket, 2004, 'JSON 格式错误')
            continue

        cmd = msg.get('cmd', '')

        try:
            if cmd == 'REPORT_AGENTS':
                await _handle_report_agents(
                    websocket, node_id, user_hasn_id,
                    msg.get('agents', []), reported_agents,
                )

            elif cmd == 'ADD_AGENT':
                await _handle_add_agent(
                    websocket, node_id, user_hasn_id,
                    msg.get('hasn_id', ''), reported_agents,
                )

            elif cmd == 'REMOVE_AGENT':
                hasn_id = msg.get('hasn_id', '')
                await ws_router.remove_agent(node_id, hasn_id)
                reported_agents.discard(hasn_id)

            elif cmd == 'SEND':
                await _handle_send(
                    websocket, node_id, user_hasn_id,
                    msg, reported_agents,
                )

            elif cmd == 'READ':
                await _handle_read(msg, user_hasn_id)

            elif cmd == 'TYPING':
                await _handle_typing(user_hasn_id, msg)

            elif cmd == 'PING':
                await websocket.send_json({
                    'cmd': 'PONG',
                    'ts': msg.get('ts'),
                })

            else:
                await _send_error(websocket, 2003, f'未知命令: {cmd}')

        except Exception as e:
            log.error(f'处理命令 {cmd} 异常: {e}', exc_info=True)
            await _send_error(websocket, 9001, f'服务器内部错误')


async def _handle_report_agents(
    websocket: WebSocket,
    node_id: str,
    user_hasn_id: str,
    agents: list[dict],
    reported_agents: set[str],
) -> None:
    """处理 REPORT_AGENTS 命令"""
    async with async_db_session() as db:
        result = await ws_router.report_agents(node_id, user_hasn_id, agents, db)

    # 更新本地记录
    for aid in result['accepted']:
        reported_agents.add(aid)

    await websocket.send_json({
        'cmd': 'REPORT_AGENTS_ACK',
        **result,
    })

    # 补推离线消息
    offline_msgs = await ws_router.get_offline_messages(
        user_hasn_id, list(reported_agents)
    )
    if offline_msgs:
        await websocket.send_json({
            'cmd': 'OFFLINE_MESSAGES',
            'messages': offline_msgs,
        })


async def _handle_add_agent(
    websocket: WebSocket,
    node_id: str,
    user_hasn_id: str,
    hasn_id: str,
    reported_agents: set[str],
) -> None:
    """处理 ADD_AGENT 命令"""
    async with async_db_session() as db:
        result = await ws_router.add_agent(node_id, user_hasn_id, hasn_id, db)

    if result.get('accepted'):
        reported_agents.add(hasn_id)

    await websocket.send_json({
        'cmd': 'ADD_AGENT_ACK',
        **result,
    })


async def _handle_send(
    websocket: WebSocket,
    node_id: str,
    user_hasn_id: str,
    msg: dict,
    reported_agents: set[str],
) -> None:
    """处理 SEND 命令"""
    from_id = msg.get('from_id', user_hasn_id)
    to_target = msg.get('to', '')
    content = msg.get('content', {})
    local_id = msg.get('local_id')
    content_type = msg.get('content_type', 1)
    msg_type = msg.get('msg_type', 'message')
    reply_to_id = msg.get('reply_to_id')

    # 校验 from_id 合法性
    if from_id != user_hasn_id and from_id not in reported_agents:
        await _send_error(websocket, 2010, f'未授权的 from_id: {from_id}')
        return

    if not to_target:
        await _send_error(websocket, 2002, '缺少目标地址 (to)')
        return

    # 处理 content 格式
    if isinstance(content, str):
        content = {'text': content}
    elif isinstance(content, dict) and 'type' in content:
        if content.get('type') == 'text' and 'text' in content:
            content_type = 1

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
    await websocket.send_json({
        'cmd': 'ACK',
        'msg_id': result['msg_id'],
        'conversation_id': result['conversation_id'],
        'local_id': local_id,
        'status': 'sent',
    })

    # 同时推送给发送方自己的其他节点（多端同步）
    sender_payload = {
        'cmd': 'MESSAGE',
        'to_id': user_hasn_id,
        'message': {
            'id': result['msg_id'],
            'conversation_id': result['conversation_id'],
            'from_id': from_id,
            'to_id': to_target,
            'content_type': content_type,
            'content': content,
            'msg_type': msg_type,
            'status': 1,
            'local_id': local_id,
            'self_sent': True,
        },
    }
    from backend.database.redis import redis_client
    from backend.app.hasn.service.ws_router import USER_NODES_PREFIX
    other_nodes = await redis_client.smembers(f'{USER_NODES_PREFIX}:{user_hasn_id}')
    for nid in other_nodes:
        if nid != node_id:
            other_ws = _ws_connections.get(nid)
            if other_ws:
                try:
                    await other_ws.send_json(sender_payload)
                except Exception:
                    pass


async def _handle_read(msg: dict, user_hasn_id: str) -> None:
    """处理 READ 命令"""
    conversation_id = msg.get('conversation_id', '')
    last_msg_id = msg.get('last_msg_id', 0)

    if not conversation_id:
        return

    async with async_db_session() as db:
        await message_router.mark_read(db, user_hasn_id, conversation_id, last_msg_id)

    # TODO: 推送已读回执给对方


async def _handle_typing(user_hasn_id: str, msg: dict) -> None:
    """处理 TYPING 命令"""
    conversation_id = msg.get('conversation_id', '')
    to_id = msg.get('to_id', '')

    if not to_id:
        return

    typing_payload = {
        'cmd': 'TYPING',
        'from_id': user_hasn_id,
        'conversation_id': conversation_id,
    }
    await ws_router.push_message_to(to_id, typing_payload)


async def _send_error(websocket: WebSocket, code: int, message: str) -> None:
    """发送错误消息"""
    await websocket.send_json({
        'cmd': 'ERROR',
        'code': code,
        'message': message,
    })
