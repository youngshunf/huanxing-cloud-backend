"""
HASN WebSocket 路由服务 — 在线状态管理
对应设计文档: 06-数据模型.md Redis §3.2
"""
from backend.database.redis import redis_client
from backend.common.log import log


class WSRouterService:
    """管理 hasn_id → WebSocket sid 的映射"""

    # 对齐设计文档: HASH hasn:ws:connections
    CONN_KEY = "hasn:ws:connections"
    # 对齐设计文档: HASH hasn:presence
    PRESENCE_KEY = "hasn:presence"

    @classmethod
    async def register_client(cls, hasn_id: str, sid: str) -> None:
        """客户端连上 WS 时注册"""
        await redis_client.hset(cls.CONN_KEY, hasn_id, sid)
        await redis_client.hset(cls.PRESENCE_KEY, hasn_id, '{"status":"online"}')
        log.info(f"[HASN WS] 上线: {hasn_id} -> sid={sid}")

    @classmethod
    async def unregister_client(cls, hasn_id: str) -> None:
        """客户端断开时清理"""
        await redis_client.hdel(cls.CONN_KEY, hasn_id)
        await redis_client.hdel(cls.PRESENCE_KEY, hasn_id)
        log.info(f"[HASN WS] 下线: {hasn_id}")

    @classmethod
    async def get_client_sid(cls, hasn_id: str) -> str | None:
        """查找目标 hasn_id 的 WebSocket sid"""
        sid = await redis_client.hget(cls.CONN_KEY, hasn_id)
        if sid:
            return sid.decode('utf-8') if isinstance(sid, bytes) else str(sid)
        return None

    @classmethod
    async def is_online(cls, hasn_id: str) -> bool:
        return await redis_client.hexists(cls.CONN_KEY, hasn_id)


ws_router = WSRouterService()
