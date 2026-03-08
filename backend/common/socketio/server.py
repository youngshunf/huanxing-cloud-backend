"""
SocketIO 服务器实例 + 连接/断开事件
对应设计文档: 02-通信协议.md §三 WebSocket 协议
"""
import urllib.parse

import socketio

from backend.common.log import log
from backend.common.security.jwt import jwt_authentication
from backend.core.conf import settings
from backend.database.redis import redis_client

# 创建 Socket.IO 服务器实例
sio = socketio.AsyncServer(
    client_manager=socketio.AsyncRedisManager(
        f'redis://:{urllib.parse.quote(settings.REDIS_PASSWORD)}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DATABASE}',
    ),
    async_mode='asgi',
    cors_allowed_origins=[],
    namespaces=['/ws'],
)


@sio.event
async def connect(sid, environ, auth) -> bool:
    """
    Socket 连接事件
    对应设计文档 §3.1: Human 用 JWT, Agent 用 API Key
    """
    if not auth:
        log.error('WebSocket 连接失败: 无授权')
        return False

    session_uuid = auth.get('session_uuid')
    hasn_id = auth.get('hasn_id')  # HASN hasn_id (h_xxx 或 a_xxx)
    token = auth.get('token')

    # ── HASN 连接: hasn_id + (token 或 api_key) ──
    if hasn_id:
        from backend.app.hasn_core.service.ws_router import ws_router
        await ws_router.register_client(hasn_id, sid)
        # sid → hasn_id 反向映射，断开时用
        await redis_client.set(f"hasn:ws:sid2id:{sid}", hasn_id, ex=86400)

        # 上线后推送离线消息
        import json
        offline_key = f"hasn:offline:{hasn_id}"
        offline_msgs = await redis_client.lrange(offline_key, 0, -1)
        if offline_msgs:
            for raw in offline_msgs:
                msg = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                await sio.emit('hasn_message_push', json.loads(msg), to=sid)
            await redis_client.delete(offline_key)
            log.info(f"[HASN WS] 补推 {len(offline_msgs)} 条离线消息给 {hasn_id}")

        return True

    # ── 传统连接 (唤星既有系统) ──
    if not token or not session_uuid:
        log.error('WebSocket 连接失败: 授权失败')
        return False

    if token == settings.WS_NO_AUTH_MARKER:
        await redis_client.sadd(settings.TOKEN_ONLINE_REDIS_PREFIX, session_uuid)
        return True

    try:
        await jwt_authentication(token)
    except Exception as e:
        log.info(f'WebSocket 连接失败: {e!s}')
        return False

    await redis_client.sadd(settings.TOKEN_ONLINE_REDIS_PREFIX, session_uuid)
    return True


@sio.event
async def disconnect(sid) -> None:
    """Socket 断开连接事件"""
    # 清理传统会话
    await redis_client.spop(settings.TOKEN_ONLINE_REDIS_PREFIX)

    # 清理 HASN 会话
    hasn_id_raw = await redis_client.get(f"hasn:ws:sid2id:{sid}")
    if hasn_id_raw:
        hasn_id = hasn_id_raw.decode('utf-8') if isinstance(hasn_id_raw, bytes) else str(hasn_id_raw)
        from backend.app.hasn_core.service.ws_router import ws_router
        await ws_router.unregister_client(hasn_id)
        await redis_client.delete(f"hasn:ws:sid2id:{sid}")
