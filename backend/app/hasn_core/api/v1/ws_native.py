"""
HASN 原生 WebSocket 端点 (供桌面端/APP使用)
替代 Socket.IO 协议，直接走标准 WebSocket + JSON

路径: /api/v1/hasn/ws/native
认证: query参数 token=xxx (HASN JWT)

与 Socket.IO 共用:
  - Redis 在线状态 (hasn:ws:connections)
  - Redis 推送队列 (hasn:push:{hasn_id})
  - Redis 离线队列 (hasn:offline:{hasn_id})
  - Redis 未读计数 (hasn:unread:{hasn_id})

上行消息 (客户端 → 服务端):
  {"cmd": "SEND", "to_id": "h_xxx", "content": "你好", "content_type": 1}
  {"cmd": "READ", "conversation_id": "uuid", "last_msg_id": 12345}
  {"cmd": "PING", "ts": 1741488000}

下行消息 (服务端 → 客户端):
  {"cmd": "MESSAGE", "message": {...}}
  {"cmd": "ACK", "msg_id": 123, "conversation_id": "uuid", "local_id": "xxx"}
  {"cmd": "PONG", "ts": 1741488000}
  {"cmd": "ERROR", "code": 2001, "message": "..."}
"""
import asyncio
import json
from contextlib import suppress

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from backend.common.log import log
from backend.database.redis import redis_client
from backend.app.hasn_core.service.hasn_auth import hasn_verify_jwt
from backend.app.hasn_core.service.ws_router import ws_router

router = APIRouter(prefix="/ws", tags=["HASN WebSocket"])

# 存储 hasn_id → WebSocket 对象 (原生WS连接, 与Socket.IO的sid映射分开)
_native_ws_clients: dict[str, WebSocket] = {}


async def _push_loop(websocket: WebSocket, hasn_id: str):
    """
    推送循环: 从 Redis 队列拉取消息推送给客户端

    复用与 Socket.IO 相同的 Redis key:
    - hasn:push:{hasn_id} — 在线推送队列 (messages.py send_message 写入)
    """
    push_key = f"hasn:push:{hasn_id}"

    while True:
        try:
            # BLPOP 带超时, 无消息时每30秒发心跳
            result = await redis_client.blpop(push_key, timeout=30)
            if result:
                _, raw = result
                msg_str = raw.decode('utf-8') if isinstance(raw, bytes) else str(raw)
                await websocket.send_text(msg_str)
            else:
                # 超时无消息 → 发心跳保活
                await websocket.send_json({"cmd": "PONG", "ts": 0})
        except (WebSocketDisconnect, RuntimeError):
            break
        except Exception as e:
            log.error(f"[HASN NativeWS] 推送异常: {hasn_id} - {e}")
            break


async def _recv_loop(websocket: WebSocket, hasn_id: str, auth_info: dict):
    """
    接收循环: 处理客户端上行消息

    支持的命令:
    - SEND: 发送消息 (复用 messages API 的核心逻辑)
    - READ: 标记已读
    - PING: 心跳
    """
    while True:
        try:
            text = await websocket.receive_text()
            data = json.loads(text)
            cmd = data.get('cmd', '').upper()

            if cmd == 'SEND':
                await _handle_send(websocket, hasn_id, auth_info, data)
            elif cmd == 'READ':
                await _handle_read(hasn_id, data)
            elif cmd == 'PING':
                await websocket.send_json({"cmd": "PONG", "ts": data.get("ts", 0)})
            else:
                await websocket.send_json({
                    "cmd": "ERROR",
                    "code": 2003,
                    "message": f"未知命令: {cmd}",
                })

        except (WebSocketDisconnect, RuntimeError):
            break
        except json.JSONDecodeError:
            await websocket.send_json({
                "cmd": "ERROR",
                "code": 2004,
                "message": "无效的 JSON 格式",
            })
        except Exception as e:
            log.error(f"[HASN NativeWS] 接收异常: {hasn_id} - {e}")
            await websocket.send_json({
                "cmd": "ERROR",
                "code": 5000,
                "message": str(e),
            })


async def _handle_send(websocket: WebSocket, hasn_id: str, auth_info: dict, data: dict):
    """
    处理 SEND 命令 — 逻辑与 messages.py send_message 一致

    上行: {"cmd":"SEND", "to":"100002", "content":"你好", "content_type":1, "local_id":"uuid"}
    下行: {"cmd":"ACK", "msg_id":123, "conversation_id":"uuid", "local_id":"uuid", "status":"sent"}
    """
    from backend.database.db import async_db_session
    from backend.app.hasn_social.service.route_guard import route_guard
    from backend.app.hasn_core.crud.crud_message import crud_hasn_message
    from backend.app.hasn_core.crud.crud_conversation import crud_hasn_conversation
    from backend.app.hasn_core.crud.crud_human import crud_hasn_human
    from backend.app.hasn_core.crud.crud_agent import crud_hasn_agent

    to_star_id = data.get('to')
    content = data.get('content', '')
    content_type = data.get('content_type', 1)
    local_id = data.get('local_id')  # 客户端本地消息ID，原样回传

    if not to_star_id or not content:
        await websocket.send_json({
            "cmd": "ERROR", "code": 2002,
            "message": "缺少必要字段: to, content",
        })
        return

    entity_type = auth_info["type"]

    async with async_db_session() as db:
        # 1. 解析目标唤星号
        target, target_type, target_owner_id = None, None, None
        if '#' in to_star_id:
            agent = await crud_hasn_agent.get_by_star_id(db, to_star_id)
            if agent:
                target, target_type, target_owner_id = agent, 'agent', agent.owner_id
        else:
            human = await crud_hasn_human.get_by_star_id(db, to_star_id)
            if human:
                target, target_type, target_owner_id = human, 'human', human.id

        if not target:
            await websocket.send_json({
                "cmd": "ERROR", "code": 2005,
                "message": f"唤星号 {to_star_id} 不存在",
            })
            return

        if target.id == hasn_id:
            await websocket.send_json({
                "cmd": "ERROR", "code": 2006,
                "message": "不能给自己发消息",
            })
            return

        # 2. 权限检查
        sender_owner_id = None
        if entity_type == "agent":
            sender_entity = await crud_hasn_agent.get_by_id(db, hasn_id)
            if sender_entity:
                sender_owner_id = sender_entity.owner_id

        perm_s = sender_owner_id if entity_type == 'agent' and sender_owner_id else hasn_id
        perm_r = target_owner_id

        if perm_s != perm_r:
            allowed = await route_guard.check_permission(db, perm_s, perm_r)
            if not allowed:
                await websocket.send_json({
                    "cmd": "ERROR", "code": 2001,
                    "message": f"没有权限给 {to_star_id} 发消息，请先添加好友",
                })
                return

        # 3. 获取/创建会话
        conv = await crud_hasn_conversation.get_or_create_direct(db, hasn_id, target.id)

        # 4. 创建消息
        from_type = 1 if entity_type == "human" else 2
        msg = await crud_hasn_message.create(
            db,
            conversation_id=conv.id,
            from_id=hasn_id,
            from_type=from_type,
            content=content,
            content_type=content_type,
        )

        # 5. 更新会话最后消息
        await crud_hasn_conversation.update_last_message(db, conv.id, content)
        await db.commit()
        await db.refresh(msg)

        # 6. 推送给接收方 (写入 Redis 队列, push_loop 或 Socket.IO 会消费)
        msg_payload = json.dumps({
            "cmd": "MESSAGE",
            "message": {
                "id": msg.id,
                "conversation_id": conv.id,
                "from_id": hasn_id,
                "from_star_id": auth_info["star_id"],
                "from_type": from_type,
                "content": content,
                "content_type": content_type,
                "created_at": str(msg.created_time) if msg.created_time else None,
            },
        })

        # 写入目标的推送队列 (无论对方用原生WS还是Socket.IO都能收到)
        target_sid = await ws_router.get_client_sid(target.id)
        if target_sid:
            # 对方在线 → 推入推送队列
            await redis_client.rpush(f"hasn:push:{target.id}", msg_payload)
        else:
            # 对方离线 → 推入离线队列
            await redis_client.rpush(f"hasn:offline:{target.id}", msg_payload)
            await redis_client.expire(f"hasn:offline:{target.id}", 7 * 86400)

        # 7. 更新未读数
        await redis_client.hincrby(f"hasn:unread:{target.id}", conv.id, 1)

        # 8. ACK 回执 (包含 local_id 供客户端关联)
        await websocket.send_json({
            "cmd": "ACK",
            "msg_id": msg.id,
            "conversation_id": conv.id,
            "local_id": local_id,
            "status": "sent",
        })


async def _handle_read(hasn_id: str, data: dict):
    """处理 READ 命令"""
    from backend.database.db import async_db_session
    from backend.app.hasn_core.crud.crud_message import crud_hasn_message

    conversation_id = data.get('conversation_id')
    last_msg_id = data.get('last_msg_id')

    if not conversation_id or not last_msg_id:
        return

    async with async_db_session() as db:
        await crud_hasn_message.mark_read(db, conversation_id, last_msg_id)
        await db.commit()

    # 清除未读计数
    await redis_client.hdel(f"hasn:unread:{hasn_id}", conversation_id)


# ═══════════════════════════════════════════════════
# WebSocket 端点
# ═══════════════════════════════════════════════════

@router.websocket("/native")
async def hasn_native_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="HASN JWT Token"),
):
    """
    原生 WebSocket 端点

    连接: ws(s)://api.huanxing.dcfuture.cn/api/v1/hasn/ws/native?token=xxx
    """
    # 1. 验证 token
    try:
        auth_info = hasn_verify_jwt(token)
        hasn_id = auth_info["hasn_id"]
        log.info(f"[HASN NativeWS] 连接: {hasn_id}")
    except Exception as e:
        log.warning(f"[HASN NativeWS] 认证失败: {e}")
        await websocket.close(code=4001, reason="认证失败")
        return

    # 2. 接受连接
    await websocket.accept()

    # 3. 注册在线状态 (复用 ws_router, 和 Socket.IO 共享)
    # 用 "native:{hasn_id}" 做 sid, 区分于 Socket.IO 的 sid
    native_sid = f"native:{hasn_id}"
    await ws_router.register_client(hasn_id, native_sid)
    _native_ws_clients[hasn_id] = websocket

    try:
        # 4. 补推离线消息
        offline_key = f"hasn:offline:{hasn_id}"
        offline_msgs = await redis_client.lrange(offline_key, 0, -1)
        if offline_msgs:
            for raw in offline_msgs:
                msg_str = raw.decode('utf-8') if isinstance(raw, bytes) else str(raw)
                await websocket.send_text(msg_str)
            await redis_client.delete(offline_key)
            log.info(f"[HASN NativeWS] 补推 {len(offline_msgs)} 条离线消息给 {hasn_id}")

        # 5. 启动双向收发循环
        push_task = asyncio.create_task(_push_loop(websocket, hasn_id))
        recv_task = asyncio.create_task(_recv_loop(websocket, hasn_id, auth_info))

        # 任一循环退出 → 全部取消
        done, pending = await asyncio.wait(
            [push_task, recv_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    except WebSocketDisconnect:
        log.info(f"[HASN NativeWS] 断开: {hasn_id}")
    except Exception as e:
        log.error(f"[HASN NativeWS] 异常: {hasn_id} - {e}")
    finally:
        # 6. 清理
        await ws_router.unregister_client(hasn_id)
        _native_ws_clients.pop(hasn_id, None)
        log.info(f"[HASN NativeWS] 清理完毕: {hasn_id}")
