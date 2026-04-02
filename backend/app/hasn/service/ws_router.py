"""HASN WebSocket 连接管理服务

统一节点架构 (v4.0)：所有接入 HASN 的实体都是 Node，不区分 client/gateway。

Redis 数据结构：
  hasn:node_conn              HASH  node_id → JSON{node_type, capacity, connected_at}
  hasn:user_nodes:{hasn_id}   SET   {node_id, ...}    (一个用户的所有在线节点)
  hasn:agent_node             HASH  agent_hasn_id → node_id  (Agent → 宿主节点)
  hasn:push:{node_id}         LIST  待推消息队列

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

# Redis 键前缀（统一节点模型）
NODE_CONN_KEY = 'hasn:node_conn'
USER_NODES_PREFIX = 'hasn:user_nodes'
AGENT_NODE_KEY = 'hasn:agent_node'
PUSH_PREFIX = 'hasn:push'
OFFLINE_PREFIX = 'hasn:offline'
OFFLINE_TTL = 7 * 86400  # 7 天

# 兼容别名（旧代码过渡期引用）
CLIENT_CONN_KEY = NODE_CONN_KEY
USER_CLIENTS_PREFIX = USER_NODES_PREFIX
AGENT_CLIENT_KEY = AGENT_NODE_KEY


class WsRouterService:
    """WebSocket 连接路由管理（统一节点模型）"""

    # ─── 节点连接管理 ───

    async def register_node(
        self,
        node_id: str,
        user_hasn_id: str,
        node_type: str,
        ws: WebSocket,
        capacity: int = 1,
    ) -> None:
        """注册节点在线"""
        conn_info = json.dumps({
            'user_hasn_id': user_hasn_id,
            'node_type': node_type,
            'capacity': capacity,
            'connected_at': timezone.now().isoformat(),
        })
        await redis_client.hset(NODE_CONN_KEY, node_id, conn_info)
        await redis_client.sadd(f'{USER_NODES_PREFIX}:{user_hasn_id}', node_id)

        # 存储 WebSocket 引用（进程内，用于直接推送）
        _ws_connections[node_id] = ws

    # 兼容别名
    async def register_client(self, client_id, user_hasn_id, client_type, ws):
        await self.register_node(client_id, user_hasn_id, client_type, ws)

    async def unregister_node(
        self,
        node_id: str,
        user_hasn_id: str,
    ) -> None:
        """注销节点，清理 Agent 绑定"""
        # 清理该节点上报的所有 Agent
        all_agents = await redis_client.hgetall(AGENT_NODE_KEY)
        for agent_id, nid in all_agents.items():
            if nid == node_id:
                await redis_client.hdel(AGENT_NODE_KEY, agent_id)

        await redis_client.hdel(NODE_CONN_KEY, node_id)
        await redis_client.srem(f'{USER_NODES_PREFIX}:{user_hasn_id}', node_id)

        # 移除 WebSocket 引用
        _ws_connections.pop(node_id, None)

    # 兼容别名
    async def unregister_client(self, client_id, user_hasn_id):
        await self.unregister_node(client_id, user_hasn_id)

    # ─── Agent 上报管理 ───

    async def report_agents(
        self,
        node_id: str,
        user_hasn_id: str,
        agents: list[dict],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        处理 REPORT_AGENTS 命令（统一节点模型）

        校验规则：
        1. Agent 存在且 status=active
        2. Agent 归属当前用户（owner_id 匹配）
        3. 未被其他节点上报（先到先得）
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

            # 检查是否已被其他节点上报
            existing_node = await redis_client.hget(AGENT_NODE_KEY, hasn_id)
            if existing_node and existing_node != node_id:
                failed.append({
                    'hasn_id': hasn_id,
                    'reason': f'已在节点 {existing_node} 上运行',
                })
                continue

            # 注册到统一路由表
            await redis_client.hset(AGENT_NODE_KEY, hasn_id, node_id)
            accepted.append(hasn_id)

        return {'accepted': accepted, 'failed': failed}

    async def add_agent(
        self,
        node_id: str,
        user_hasn_id: str,
        hasn_id: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """动态新增 Agent"""
        result = await self.report_agents(
            node_id, user_hasn_id, [{'hasn_id': hasn_id}], db
        )
        if result['accepted']:
            return {'hasn_id': hasn_id, 'accepted': True}
        reason = result['failed'][0]['reason'] if result['failed'] else '未知错误'
        return {'hasn_id': hasn_id, 'accepted': False, 'reason': reason}

    async def remove_agent(self, node_id: str, hasn_id: str) -> None:
        """动态移除 Agent"""
        existing = await redis_client.hget(AGENT_NODE_KEY, hasn_id)
        if existing == node_id:
            await redis_client.hdel(AGENT_NODE_KEY, hasn_id)

    # ─── 消息推送 ───

    async def push_message_to(self, target_hasn_id: str, payload: dict) -> bool:
        """
        统一消息推送入口（统一节点模型）

        返回 True 表示在线推送成功，False 表示进入离线队列
        """
        payload_json = json.dumps(payload, ensure_ascii=False)
        target_type = 'human' if target_hasn_id.startswith('h_') else 'agent'

        if target_type == 'human':
            return await self._push_to_human(target_hasn_id, payload_json)
        else:
            return await self._push_to_agent(target_hasn_id, payload_json)

    async def _push_to_human(self, hasn_id: str, payload_json: str) -> bool:
        """人类消息 → 广播所有在线节点"""
        node_ids = await redis_client.smembers(f'{USER_NODES_PREFIX}:{hasn_id}')
        pushed = False

        for nid in node_ids:
            conn = await redis_client.hget(NODE_CONN_KEY, nid)
            if conn:
                # 尝试直接 WebSocket 推送
                ws = _ws_connections.get(nid)
                if ws:
                    try:
                        await ws.send_text(payload_json)
                        pushed = True
                        continue
                    except Exception:
                        pass
                # 回退到 Redis 队列
                await redis_client.rpush(f'{PUSH_PREFIX}:{nid}', payload_json)
                pushed = True

        if not pushed:
            await self._enqueue_offline(hasn_id, payload_json)

        return pushed

    async def _push_to_agent(self, hasn_id: str, payload_json: str) -> bool:
        """Agent 消息 → 查统一路由表 hasn:agent_node（不区分桌面端/云端）"""
        # 注入 to_id 字段
        payload = json.loads(payload_json)
        payload['to_id'] = hasn_id
        payload_json = json.dumps(payload, ensure_ascii=False)

        # 查统一路由表（不再区分 Gateway/Client）
        node_id = await redis_client.hget(AGENT_NODE_KEY, hasn_id)
        if node_id:
            ws = _ws_connections.get(node_id)
            if ws:
                try:
                    await ws.send_text(payload_json)
                    return True
                except Exception:
                    pass
            # WS 不可用 → Redis 队列
            await redis_client.rpush(f'{PUSH_PREFIX}:{node_id}', payload_json)
            return True

        # 离线
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
        nodes = await redis_client.smembers(f'{USER_NODES_PREFIX}:{hasn_id}')
        return len(nodes) > 0

    async def is_agent_online(self, hasn_id: str) -> bool:
        """查询 Agent 是否在线（统一查路由表）"""
        node = await redis_client.hget(AGENT_NODE_KEY, hasn_id)
        return node is not None

    async def get_entity_status(self, hasn_id: str) -> str:
        """获取实体在线状态"""
        if hasn_id.startswith('h_'):
            return 'online' if await self.is_human_online(hasn_id) else 'offline'
        else:
            return 'online' if await self.is_agent_online(hasn_id) else 'offline'


# 进程内 WebSocket 连接引用（node_id → WebSocket）
_ws_connections: dict[str, WebSocket] = {}

# 全局单例
ws_router: WsRouterService = WsRouterService()
