"""HASN WebSocket 连接管理服务

管理客户端和 Gateway 的在线状态，对齐 29 文档 §5.3 Redis 数据结构：

客户端连接（desktop/mobile/web）:
  hasn:client_conn            HASH  client_id → JSON{user_hasn_id, client_type, connected_at}
  hasn:user_clients:{hasn_id} SET   {client_id, ...}
  hasn:agent_client           HASH  agent_hasn_id → client_id
  hasn:push:{client_id}       LIST  待推消息队列

Gateway 连接（cloud）:
  hasn:gw:conns               HASH  conn_id → JSON{server_id, agent_count}
  hasn:gw:conns_by_server     HASH  server_id → conn_id
  hasn:gw:agents              HASH  agent_hasn_id → conn_id
  hasn:push:{conn_id}         LIST  待推消息队列

离线消息:
  hasn:offline:{hasn_id}      LIST  (7天 TTL)
"""

import json
from datetime import datetime
from typing import Any

from fastapi import WebSocket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.redis import redis_client
from backend.utils.timezone import timezone

from backend.app.hasn.model.hasn_agents import HasnAgents

# Redis 键前缀
CLIENT_CONN_KEY = 'hasn:client_conn'
USER_CLIENTS_PREFIX = 'hasn:user_clients'
AGENT_CLIENT_KEY = 'hasn:agent_client'
GW_AGENTS_KEY = 'hasn:gw:agents'
PUSH_PREFIX = 'hasn:push'
OFFLINE_PREFIX = 'hasn:offline'
OFFLINE_TTL = 7 * 86400  # 7 天


class WsRouterService:
    """WebSocket 连接路由管理"""

    # ─── 客户端连接管理 ───

    async def register_client(
        self,
        client_id: str,
        user_hasn_id: str,
        client_type: str,
        ws: WebSocket,
    ) -> None:
        """注册客户端在线"""
        conn_info = json.dumps({
            'user_hasn_id': user_hasn_id,
            'client_type': client_type,
            'connected_at': timezone.now().isoformat(),
        })
        await redis_client.hset(CLIENT_CONN_KEY, client_id, conn_info)
        await redis_client.sadd(f'{USER_CLIENTS_PREFIX}:{user_hasn_id}', client_id)

        # 存储 WebSocket 引用（进程内，用于直接推送）
        _ws_connections[client_id] = ws

    async def unregister_client(
        self,
        client_id: str,
        user_hasn_id: str,
    ) -> None:
        """注销客户端，清理 Agent 绑定"""
        # 清理该客户端上报的所有 Agent
        all_agents = await redis_client.hgetall(AGENT_CLIENT_KEY)
        for agent_id, cid in all_agents.items():
            if cid == client_id:
                await redis_client.hdel(AGENT_CLIENT_KEY, agent_id)

        await redis_client.hdel(CLIENT_CONN_KEY, client_id)
        await redis_client.srem(f'{USER_CLIENTS_PREFIX}:{user_hasn_id}', client_id)

        # 移除 WebSocket 引用
        _ws_connections.pop(client_id, None)

    # ─── Agent 上报管理 ───

    async def report_agents(
        self,
        client_id: str,
        user_hasn_id: str,
        agents: list[dict],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        处理 REPORT_AGENTS 命令

        校验规则（对齐 29 文档 §4.5）：
        1. Agent 存在且 status=active
        2. Agent 归属当前用户（owner_id 匹配）
        3. 未被其他客户端上报（先到先得）
        """
        accepted = []
        failed = []

        for agent_info in agents:
            hasn_id = agent_info.get('hasn_id', '')

            # 查询 Agent 记录
            result = await db.execute(
                select(HasnAgents).where(HasnAgents.hasn_id == hasn_id)
            )
            agent = result.scalar_one_or_none()

            if not agent:
                failed.append({'hasn_id': hasn_id, 'reason': 'Agent 不存在'})
                continue
            if agent.owner_id != user_hasn_id:
                failed.append({'hasn_id': hasn_id, 'reason': '非本用户 Agent'})
                continue
            if agent.status != 'active':
                failed.append({'hasn_id': hasn_id, 'reason': 'Agent 已停用'})
                continue

            # 检查是否已被其他客户端上报
            existing_client = await redis_client.hget(AGENT_CLIENT_KEY, hasn_id)
            if existing_client and existing_client != client_id:
                failed.append({
                    'hasn_id': hasn_id,
                    'reason': f'已在客户端 {existing_client} 上运行',
                })
                continue

            # 注册
            await redis_client.hset(AGENT_CLIENT_KEY, hasn_id, client_id)
            accepted.append(hasn_id)

        return {'accepted': accepted, 'failed': failed}

    async def add_agent(
        self,
        client_id: str,
        user_hasn_id: str,
        hasn_id: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """动态新增 Agent"""
        result = await self.report_agents(
            client_id, user_hasn_id, [{'hasn_id': hasn_id}], db
        )
        if result['accepted']:
            return {'hasn_id': hasn_id, 'accepted': True}
        reason = result['failed'][0]['reason'] if result['failed'] else '未知错误'
        return {'hasn_id': hasn_id, 'accepted': False, 'reason': reason}

    async def remove_agent(self, client_id: str, hasn_id: str) -> None:
        """动态移除 Agent"""
        existing = await redis_client.hget(AGENT_CLIENT_KEY, hasn_id)
        if existing == client_id:
            await redis_client.hdel(AGENT_CLIENT_KEY, hasn_id)

    # ─── 消息推送 ───

    async def push_message_to(self, target_hasn_id: str, payload: dict) -> bool:
        """
        统一消息推送入口（对齐 29 文档 §5.1）

        返回 True 表示在线推送成功，False 表示进入离线队列
        """
        payload_json = json.dumps(payload, ensure_ascii=False)
        target_type = 'human' if target_hasn_id.startswith('h_') else 'agent'

        if target_type == 'human':
            return await self._push_to_human(target_hasn_id, payload_json)
        else:
            return await self._push_to_agent(target_hasn_id, payload_json)

    async def _push_to_human(self, hasn_id: str, payload_json: str) -> bool:
        """人类消息 → 广播所有在线客户端"""
        client_ids = await redis_client.smembers(f'{USER_CLIENTS_PREFIX}:{hasn_id}')
        pushed = False

        for cid in client_ids:
            conn = await redis_client.hget(CLIENT_CONN_KEY, cid)
            if conn:
                # 尝试直接 WebSocket 推送
                ws = _ws_connections.get(cid)
                if ws:
                    try:
                        await ws.send_text(payload_json)
                        pushed = True
                        continue
                    except Exception:
                        pass
                # 回退到 Redis 队列
                await redis_client.rpush(f'{PUSH_PREFIX}:{cid}', payload_json)
                pushed = True

        if not pushed:
            await self._enqueue_offline(hasn_id, payload_json)

        return pushed

    async def _push_to_agent(self, hasn_id: str, payload_json: str) -> bool:
        """Agent 消息 → 先查 Gateway（云端），再查客户端（本地）"""
        # 注入 to_id 字段
        payload = json.loads(payload_json)
        payload['to_id'] = hasn_id
        payload_json = json.dumps(payload, ensure_ascii=False)

        # 1. 查 Gateway（云端 Agent）
        gw_conn = await redis_client.hget(GW_AGENTS_KEY, hasn_id)
        if gw_conn:
            await redis_client.rpush(f'{PUSH_PREFIX}:{gw_conn}', payload_json)
            return True

        # 2. 查客户端（本地 Agent）
        client_id = await redis_client.hget(AGENT_CLIENT_KEY, hasn_id)
        if client_id:
            ws = _ws_connections.get(client_id)
            if ws:
                try:
                    await ws.send_text(payload_json)
                    return True
                except Exception:
                    pass
            await redis_client.rpush(f'{PUSH_PREFIX}:{client_id}', payload_json)
            return True

        # 3. 离线
        await self._enqueue_offline(hasn_id, payload_json)
        return False

    async def _enqueue_offline(self, hasn_id: str, payload_json: str) -> None:
        """消息入离线队列"""
        key = f'{OFFLINE_PREFIX}:{hasn_id}'
        await redis_client.rpush(key, payload_json)
        await redis_client.expire(key, OFFLINE_TTL)

    # ─── 离线消息补推 ───

    async def get_offline_messages(
        self,
        user_hasn_id: str,
        agent_ids: list[str],
    ) -> list[dict]:
        """获取并清理离线消息（用户 + Agent）"""
        all_msgs = []

        # 用户的离线消息
        user_key = f'{OFFLINE_PREFIX}:{user_hasn_id}'
        user_msgs = await redis_client.lrange(user_key, 0, -1)
        for raw in user_msgs:
            try:
                all_msgs.append(json.loads(raw))
            except (json.JSONDecodeError, TypeError):
                pass
        if user_msgs:
            await redis_client.delete(user_key)

        # 各 Agent 的离线消息
        for aid in agent_ids:
            agent_key = f'{OFFLINE_PREFIX}:{aid}'
            agent_msgs = await redis_client.lrange(agent_key, 0, -1)
            for raw in agent_msgs:
                try:
                    all_msgs.append(json.loads(raw))
                except (json.JSONDecodeError, TypeError):
                    pass
            if agent_msgs:
                await redis_client.delete(agent_key)

        # 按时间排序
        all_msgs.sort(key=lambda m: m.get('created_time', ''))
        return all_msgs

    # ─── 在线状态查询 ───

    async def is_human_online(self, hasn_id: str) -> bool:
        """查询 Human 是否在线"""
        clients = await redis_client.smembers(f'{USER_CLIENTS_PREFIX}:{hasn_id}')
        return len(clients) > 0

    async def is_agent_online(self, hasn_id: str) -> bool:
        """查询 Agent 是否在线（云端或本地）"""
        gw = await redis_client.hget(GW_AGENTS_KEY, hasn_id)
        if gw:
            return True
        client = await redis_client.hget(AGENT_CLIENT_KEY, hasn_id)
        return client is not None

    async def get_entity_status(self, hasn_id: str) -> str:
        """获取实体在线状态"""
        if hasn_id.startswith('h_'):
            return 'online' if await self.is_human_online(hasn_id) else 'offline'
        else:
            return 'online' if await self.is_agent_online(hasn_id) else 'offline'


# 进程内 WebSocket 连接引用（client_id → WebSocket）
_ws_connections: dict[str, WebSocket] = {}

# 全局单例
ws_router: WsRouterService = WsRouterService()
