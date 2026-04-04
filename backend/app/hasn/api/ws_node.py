"""HASN 统一节点 WebSocket 端点

统一实体架构 (v5.0)：
- 端点: /api/v1/hasn/ws/node?node_key=<hasn_nk_xxx>
- 所有节点类型（desktop/mobile/web/cloud）共用同一端点
- Node Key 仅验证物理节点，不绑定用户身份
- Human 和 Agent 通过 report_entities / add_entity 动态上报
- 帧格式: { "hasn": "hasn/2.0", "method": "hasn.xxx.yyy", "params": {...} }

上行命令:
  hasn.node.report_entities  — 全量上报实体（连接后）
  hasn.node.add_entity       — 增量新增实体
  hasn.node.remove_entity    — 增量移除实体
  hasn.agent.register        — 注册新 Agent（创建 DB 记录）
  hasn.agent.deregister      — 注销 Agent（标记删除）
  hasn.message.send          — 发送消息
  hasn.message.read          — 标记已读
  hasn.typing                — 正在输入
  hasn.ping                  — 心跳

下行事件:
  hasn.connected             — 连接成功
  hasn.node.report_entities_ack — 实体上报结果
  hasn.node.add_entity_ack   — 新增实体结果
  hasn.agent.register_ack    — Agent 注册结果
  hasn.message.received      — 收到消息
  hasn.node.offline_messages — 离线消息补推
  hasn.message.ack           — 发送回执
  hasn.typing                — 对方正在输入
  hasn.pong                  — 心跳回包
  hasn.error                 — 错误
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from backend.database.db import async_db_session
from backend.app.hasn.service.hasn_auth import verify_node_key, verify_client_jwt
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
    node_key: str = Query(None),
    token: str = Query(None),
    # 兼容旧参数名
    api_key: str = Query(None),
):
    """HASN 统一节点 WebSocket 端点（所有节点类型共用）"""

    # 1. 认证：Node Key 仅验证物理节点，不绑定用户
    try:
        key = node_key or api_key
        if key:
            auth = await verify_node_key(key)
        elif token:
            auth = verify_client_jwt(token)
        else:
            await websocket.close(code=4001, reason='缺少认证凭据 (node_key)')
            return
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


# ─── 兼容旧 /ws/client 端点 ───

@router.websocket('/ws/client')
async def hasn_client_websocket_compat(
    websocket: WebSocket,
    token: str = Query(...),
):
    """兼容旧 /ws/client 端点 → 内部转发到统一节点逻辑"""
    await hasn_node_websocket(websocket, token=token, node_key=None)


async def _recv_loop(
    websocket: WebSocket,
    node_id: str,
) -> None:
    """处理节点上行消息"""
    # 记录已上报的实体（用于 from_id 校验）
    reported_entities: set[str] = set()

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
            if method == 'hasn.node.report_entities':
                await _handle_report_entities(
                    websocket, node_id,
                    params.get('entities', []), reported_entities,
                )

            elif method == 'hasn.node.add_entity':
                await _handle_add_entity(
                    websocket, node_id, params, reported_entities,
                )

            elif method == 'hasn.node.remove_entity':
                hasn_id = params.get('hasn_id', '')
                await ws_router.remove_entity(node_id, hasn_id)
                reported_entities.discard(hasn_id)

            elif method == 'hasn.agent.register':
                await _handle_agent_register(
                    websocket, node_id, params, reported_entities, req_id,
                )

            elif method == 'hasn.agent.deregister':
                await _handle_agent_deregister(
                    websocket, node_id, params, reported_entities, req_id,
                )

            elif method == 'hasn.message.send':
                await _handle_send(
                    websocket, node_id, params, reported_entities,
                )

            elif method == 'hasn.message.read':
                await _handle_read(params, reported_entities)

            elif method == 'hasn.typing':
                await _handle_typing(params, reported_entities)

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

async def _handle_report_entities(
    websocket: WebSocket,
    node_id: str,
    entities: list[dict],
    reported_entities: set[str],
) -> None:
    """处理 hasn.node.report_entities"""
    async with async_db_session() as db:
        result = await ws_router.report_entities(node_id, entities, db)

    # 更新本地记录（全量替换）
    reported_entities.clear()
    for eid in result['accepted']:
        reported_entities.add(eid)

    await websocket.send_json(_frame('hasn.node.report_entities_ack', result))

    # 补推离线消息
    if reported_entities:
        offline_msgs = await ws_router.get_offline_messages(list(reported_entities))
        if offline_msgs:
            await websocket.send_json(_frame('hasn.node.offline_messages', {
                'messages': offline_msgs,
            }))


async def _handle_add_entity(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    reported_entities: set[str],
) -> None:
    """处理 hasn.node.add_entity"""
    async with async_db_session() as db:
        result = await ws_router.add_entity(node_id, params, db)

    hasn_id = params.get('hasn_id', '')
    if result.get('accepted'):
        reported_entities.add(hasn_id)

        # 补推该实体的离线消息
        offline_msgs = await ws_router.get_offline_messages([hasn_id])
        if offline_msgs:
            await websocket.send_json(_frame('hasn.node.offline_messages', {
                'messages': offline_msgs,
            }))

    await websocket.send_json(_frame('hasn.node.add_entity_ack', result))


async def _handle_agent_register(
    websocket: WebSocket,
    node_id: str,
    params: dict,
    reported_entities: set[str],
    req_id: str | None,
) -> None:
    """处理 hasn.agent.register（通过 WS 创建新 Agent）"""
    from backend.app.hasn.service.hasn_auth import register_hasn_agent

    # 确定 owner_id：显式指定 or 从已上报的 Human 推断
    owner_id = params.get('owner_id', '')
    if not owner_id:
        humans = [eid for eid in reported_entities if eid.startswith('h_')]
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
    reported_entities: set[str],
    req_id: str | None,
) -> None:
    """处理 hasn.agent.deregister（永久删除 Agent）"""
    hasn_id = params.get('hasn_id', '')
    if not hasn_id:
        await _send_error(websocket, 2002, '缺少 hasn_id')
        return

    # 先下线
    await ws_router.remove_entity(node_id, hasn_id)
    reported_entities.discard(hasn_id)

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
    reported_entities: set[str],
) -> None:
    """处理 hasn.message.send"""
    from_id = params.get('from_id', '')
    to_target = params.get('to', '')
    content = params.get('content', {})
    local_id = params.get('local_id')
    msg_type = params.get('type', 'message')
    reply_to_id = params.get('context', {}).get('reply_to')

    # 校验 from_id 合法性：必须是已上报的实体
    if from_id not in reported_entities:
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
        for eid in reported_entities:
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
                'to_id': to_target,
                'content_type': content_type,
                'content': content,
                'msg_type': msg_type,
                'status': 1,
                'local_id': local_id,
                'self_sent': True,
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


async def _handle_read(params: dict, reported_entities: set[str]) -> None:
    """处理 hasn.message.read"""
    conversation_id = params.get('conversation_id', '')
    last_msg_id = params.get('last_msg_id', 0)

    if not conversation_id:
        return

    # 用已上报实体中的第一个 Human 作为 reader
    reader = next((eid for eid in reported_entities if eid.startswith('h_')), '')
    if not reader:
        return

    async with async_db_session() as db:
        await message_router.mark_read(db, reader, conversation_id, last_msg_id)


async def _handle_typing(params: dict, reported_entities: set[str]) -> None:
    """处理 hasn.typing"""
    to_id = params.get('to_id', '')
    conversation_id = params.get('conversation_id', '')

    if not to_id:
        return

    # 用已上报的第一个 Human 作为 from_id
    from_id = params.get('from_id', '')
    if not from_id:
        from_id = next((eid for eid in reported_entities if eid.startswith('h_')), '')

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
