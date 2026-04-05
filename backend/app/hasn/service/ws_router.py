"""HASN WebSocket 连接管理服务

现行模型：
- Node 先建立物理连接
- Owner 通过 add_owner 建立在线路由资格
- Agent 通过 add_agent 建立 Presence

Redis 数据结构：
  hasn:node_conn                HASH  node_id → JSON{node_type, capacity, connected_at}
  hasn:entity_node              HASH  a_xxx → node_id  (Agent 定向路由)
  hasn:node_entities:{node_id}  SET   {hasn_id, ...}   (Node 上的在线实体；active owner + online agent)
  hasn:user_nodes:{hasn_id}     SET   {node_id, ...}   (Owner 的所有在线节点，用于广播)
  hasn:push:{node_id}           LIST  待推消息队列
  hasn:offline:{hasn_id}        LIST  (7天 TTL)
"""

import json
from typing import Any

from fastapi import WebSocket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.redis import redis_client
from backend.utils.timezone import timezone

from backend.app.hasn.model.hasn_agents import HasnAgents
from backend.app.hasn.service.hasn_auth import verify_owner_proof
from backend.app.hasn.service.hasn_node_bindings_service import hasn_node_bindings_service

# Redis 键
NODE_CONN_KEY = 'hasn:node_conn'
ENTITY_NODE_KEY = 'hasn:entity_node'
NODE_ENTITIES_PREFIX = 'hasn:node_entities'
USER_NODES_PREFIX = 'hasn:user_nodes'
PUSH_PREFIX = 'hasn:push'
OFFLINE_PREFIX = 'hasn:offline'
OFFLINE_TTL = 7 * 86400  # 7 天

# 兼容别名（旧代码过渡期引用）
AGENT_NODE_KEY = ENTITY_NODE_KEY
CLIENT_CONN_KEY = NODE_CONN_KEY
USER_CLIENTS_PREFIX = USER_NODES_PREFIX
AGENT_CLIENT_KEY = ENTITY_NODE_KEY


class WsRouterService:
    """WebSocket 连接路由管理（统一实体模型）"""

    # ─── 节点连接管理 ───

    async def register_node(
        self,
        node_id: str,
        node_type: str,
        ws: WebSocket,
        capacity: int = 1,
    ) -> None:
        """注册节点在线（不绑定任何用户身份）"""
        conn_info = json.dumps({
            'node_type': node_type,
            'capacity': capacity,
            'connected_at': timezone.now().isoformat(),
        })
        await redis_client.hset(NODE_CONN_KEY, node_id, conn_info)

        # 存储 WebSocket 引用（进程内，用于直接推送）
        _ws_connections[node_id] = ws

    async def unregister_node(self, node_id: str) -> None:
        """注销节点，清理所有实体绑定"""
        # 拿到该 Node 上的所有实体
        entity_ids = await redis_client.smembers(f'{NODE_ENTITIES_PREFIX}:{node_id}')

        for hasn_id in entity_ids:
            # 从统一路由表移除
            existing = await redis_client.hget(ENTITY_NODE_KEY, hasn_id)
            if existing == node_id:
                await redis_client.hdel(ENTITY_NODE_KEY, hasn_id)

            # 如果是 Human，从 user_nodes 移除
            if hasn_id.startswith('h_'):
                await redis_client.srem(f'{USER_NODES_PREFIX}:{hasn_id}', node_id)

        # 清理 Node 实体集合
        await redis_client.delete(f'{NODE_ENTITIES_PREFIX}:{node_id}')
        # 清理 Node 连接记录
        await redis_client.hdel(NODE_CONN_KEY, node_id)
        # 移除 WebSocket 引用
        _ws_connections.pop(node_id, None)

    # ─── 现行控制平面：Owner Binding / Agent Presence ───

    async def add_owner(
        self,
        node_id: str,
        owner_id: str,
        owner_proof: dict,
        db: AsyncSession,
    ) -> dict[str, Any]:
        proof = await verify_owner_proof(owner_id, owner_proof, node_id, db)
        binding = await hasn_node_bindings_service.add_owner_binding(
            db=db,
            node_id=node_id,
            owner_id=owner_id,
            auth_profile=proof['auth_profile'],
            scopes=proof['scopes'],
            expires_at=proof['expires_at'],
        )
        await self._register_entity(node_id, owner_id, is_human=True)
        return {
            'binding_id': binding.binding_id,
            'owner_id': owner_id,
            'accepted': True,
            'scopes': binding.scopes,
            'expires_at': binding.expires_at.isoformat() if binding.expires_at else None,
        }

    async def renew_owner(
        self,
        node_id: str,
        owner_id: str,
        owner_proof: dict,
        db: AsyncSession,
    ) -> dict[str, Any]:
        proof = await verify_owner_proof(owner_id, owner_proof, node_id, db)
        binding = await hasn_node_bindings_service.renew_owner_binding(
            db=db,
            node_id=node_id,
            owner_id=owner_id,
            expires_at=proof['expires_at'],
        )
        return {
            'binding_id': binding.binding_id,
            'owner_id': owner_id,
            'accepted': True,
            'expires_at': binding.expires_at.isoformat() if binding.expires_at else None,
        }

    async def remove_owner(
        self,
        node_id: str,
        owner_id: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        removed = await hasn_node_bindings_service.remove_owner_binding(
            db=db,
            node_id=node_id,
            owner_id=owner_id,
        )
        # 移除 human 路由
        await self.unregister_entity_route(node_id, owner_id)
        # 下线该 owner 在本节点上的 agent
        entity_ids = await redis_client.smembers(f'{NODE_ENTITIES_PREFIX}:{node_id}')
        for hasn_id in entity_ids:
            if not str(hasn_id).startswith('a_'):
                continue
            result = await db.execute(select(HasnAgents).where(HasnAgents.hasn_id == hasn_id))
            agent = result.scalar_one_or_none()
            if agent and agent.owner_id == owner_id:
                await self.unregister_entity_route(node_id, hasn_id)
        return {'owner_id': owner_id, 'accepted': bool(removed)}

    async def list_owners(self, node_id: str, db: AsyncSession) -> dict[str, Any]:
        bindings = await hasn_node_bindings_service.list_active_bindings(db=db, node_id=node_id)
        return {
            'owners': [
                {
                    'binding_id': b.binding_id,
                    'owner_id': b.owner_id,
                    'status': b.status,
                    'expires_at': b.expires_at.isoformat() if b.expires_at else None,
                }
                for b in bindings
            ]
        }

    async def add_agent_presence(
        self,
        node_id: str,
        agent_id: str,
        owner_id: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        binding = await hasn_node_bindings_service.get_active_binding(db=db, node_id=node_id, owner_id=owner_id)
        if not binding:
            return {'agent_id': agent_id, 'accepted': False, 'reason': 'owner 未绑定到当前 node'}

        err = await self._validate_agent(node_id, agent_id, {'owner_id': owner_id}, db)
        if err:
            return {'agent_id': agent_id, 'accepted': False, 'reason': err['reason']}
        await self._register_entity(node_id, agent_id, is_human=False)
        return {'agent_id': agent_id, 'accepted': True}

    async def remove_agent_presence(self, node_id: str, agent_id: str) -> dict[str, Any]:
        await self.unregister_entity_route(node_id, agent_id)
        return {'agent_id': agent_id, 'accepted': True}

    async def _validate_agent(
        self, node_id: str, hasn_id: str, entity: dict, db: AsyncSession,
    ) -> dict | None:
        """校验 Agent 实体。返回 None 表示通过。"""
        owner_id = entity.get('owner_id', '')

        # 查询 Agent 记录
        result = await db.execute(
            select(HasnAgents).where(HasnAgents.hasn_id == hasn_id)
        )
        agent = result.scalar_one_or_none()

        if not agent:
            return {'hasn_id': hasn_id, 'reason': 'Agent 不存在'}
        if agent.owner_id != owner_id:
            return {'hasn_id': hasn_id, 'reason': f'owner_id 不匹配 (期望 {agent.owner_id})'}
        if agent.status != 'active':
            return {'hasn_id': hasn_id, 'reason': 'Agent 已停用'}

        # 检查是否已被其他节点上报
        existing_node = await redis_client.hget(ENTITY_NODE_KEY, hasn_id)
        if existing_node and existing_node != node_id:
            return {'hasn_id': hasn_id, 'reason': f'已在节点 {existing_node} 上运行'}

        return None

    async def _register_entity(self, node_id: str, hasn_id: str, is_human: bool) -> None:
        """将实体注册到路由表"""
        # 统一路由表
        await redis_client.hset(ENTITY_NODE_KEY, hasn_id, node_id)
        # Node 实体集合
        await redis_client.sadd(f'{NODE_ENTITIES_PREFIX}:{node_id}', hasn_id)
        # Human 额外维护多节点集合（用于广播）
        if is_human:
            await redis_client.sadd(f'{USER_NODES_PREFIX}:{hasn_id}', node_id)

    async def unregister_entity_route(self, node_id: str, hasn_id: str) -> None:
        """内部帮助函数：从路由表移除单个在线实体"""
        existing = await redis_client.hget(ENTITY_NODE_KEY, hasn_id)
        if existing == node_id:
            await redis_client.hdel(ENTITY_NODE_KEY, hasn_id)
            await redis_client.srem(f'{NODE_ENTITIES_PREFIX}:{node_id}', hasn_id)
            if hasn_id.startswith('h_'):
                await redis_client.srem(f'{USER_NODES_PREFIX}:{hasn_id}', node_id)

    # ─── 消息推送 ───

    async def push_message_to(self, target_hasn_id: str, payload: dict) -> bool:
        """
        统一消息推送入口

        返回 True 表示在线推送成功，False 表示进入离线队列
        """
        payload_json = json.dumps(payload, ensure_ascii=False)
        target_type = 'human' if target_hasn_id.startswith('h_') else 'agent'

        if target_type == 'human':
            return await self._push_to_human(target_hasn_id, payload_json)
        else:
            return await self._push_to_entity(target_hasn_id, payload_json)

    async def _push_to_human(self, hasn_id: str, payload_json: str) -> bool:
        """Human 消息 → 广播所有在线节点"""
        node_ids = await redis_client.smembers(f'{USER_NODES_PREFIX}:{hasn_id}')
        pushed = False

        for nid in node_ids:
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

    async def _push_to_entity(self, hasn_id: str, payload_json: str) -> bool:
        """Agent/通用实体消息 → 查统一路由表"""
        node_id = await redis_client.hget(ENTITY_NODE_KEY, hasn_id)
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
        entity_ids: list[str],
    ) -> list[dict]:
        """获取并清理离线消息（所有已上报实体）"""
        all_msgs = []

        for eid in entity_ids:
            key = f'{OFFLINE_PREFIX}:{eid}'
            msgs = await redis_client.lrange(key, 0, -1)
            for raw in msgs:
                try:
                    all_msgs.append(json.loads(raw))
                except (json.JSONDecodeError, TypeError):
                    pass
            if msgs:
                await redis_client.delete(key)

        # 按时间排序
        all_msgs.sort(key=lambda m: m.get('created_time', ''))
        return all_msgs

    # ─── 在线状态查询 ───

    async def is_human_online(self, hasn_id: str) -> bool:
        nodes = await redis_client.smembers(f'{USER_NODES_PREFIX}:{hasn_id}')
        return len(nodes) > 0

    async def is_agent_online(self, hasn_id: str) -> bool:
        node = await redis_client.hget(ENTITY_NODE_KEY, hasn_id)
        return node is not None

    async def get_entity_status(self, hasn_id: str) -> str:
        if hasn_id.startswith('h_'):
            return 'online' if await self.is_human_online(hasn_id) else 'offline'
        else:
            return 'online' if await self.is_agent_online(hasn_id) else 'offline'


# 进程内 WebSocket 连接引用（node_id → WebSocket）
_ws_connections: dict[str, WebSocket] = {}

# 全局单例
ws_router: WsRouterService = WsRouterService()
