"""HASN WebSocket 连接管理服务

统一实体架构 (v5.0)：Human 和 Agent 都是一等公民，统一路由。

Redis 数据结构：
  hasn:node_conn                HASH  node_id → JSON{node_type, capacity, connected_at}
  hasn:entity_node              HASH  hasn_id → node_id  (统一路由表：h_xxx/a_xxx → 宿主节点)
  hasn:node_entities:{node_id}  SET   {hasn_id, ...}  (一个 Node 上的所有实体)
  hasn:user_nodes:{hasn_id}     SET   {node_id, ...}  (一个 Human 的所有在线节点，用于广播)
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

    # ─── 统一实体上报（全量同步） ───

    async def report_entities(
        self,
        node_id: str,
        entities: list[dict],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        处理 hasn.node.report_entities（全量同步）

        entities 格式:
        - Human: { hasn_id, entity_type: "human", auth_token }
        - Agent: { hasn_id, entity_type: "agent", owner_id }

        全量同步语义：以此列表为准，先前的旧列表整体替换。
        """
        accepted = []
        failed = []

        # 先清理该 Node 上的旧实体
        old_entities = await redis_client.smembers(f'{NODE_ENTITIES_PREFIX}:{node_id}')
        for old_id in old_entities:
            existing = await redis_client.hget(ENTITY_NODE_KEY, old_id)
            if existing == node_id:
                await redis_client.hdel(ENTITY_NODE_KEY, old_id)
            if old_id.startswith('h_'):
                await redis_client.srem(f'{USER_NODES_PREFIX}:{old_id}', node_id)
        await redis_client.delete(f'{NODE_ENTITIES_PREFIX}:{node_id}')

        # 收集本次上报的所有 Human，用于 Agent owner 自动添加
        reported_humans = set()

        for entity in entities:
            hasn_id = entity.get('hasn_id', '')
            entity_type = entity.get('entity_type', '')

            if entity_type == 'human':
                result = await self._validate_human(hasn_id, entity)
                if result:
                    failed.append(result)
                    continue
                # Human 校验通过
                await self._register_entity(node_id, hasn_id, is_human=True)
                accepted.append(hasn_id)
                reported_humans.add(hasn_id)

            elif entity_type == 'agent':
                result = await self._validate_agent(node_id, hasn_id, entity, db)
                if result:
                    failed.append(result)
                    continue
                # Agent 校验通过
                await self._register_entity(node_id, hasn_id, is_human=False)
                accepted.append(hasn_id)

                # 如果 owner 不在已上报列表中，自动添加
                owner_id = entity.get('owner_id', '')
                if owner_id and owner_id not in reported_humans:
                    await self._register_entity(node_id, owner_id, is_human=True)
                    reported_humans.add(owner_id)
                    # 不加入 accepted（隐式添加）

            else:
                failed.append({'hasn_id': hasn_id, 'reason': f'未知 entity_type: {entity_type}'})

        return {'accepted': accepted, 'failed': failed}

    async def _validate_human(self, hasn_id: str, entity: dict) -> dict | None:
        """校验 Human 实体。返回 None 表示通过，返回 dict 表示失败原因。

        auth_token 支持两种格式:
        - JWT Bearer Token: 平台用户的 access_token（通过 jwt_authentication 验证）
        - Owner Token: hasn_ot_ 前缀的持有者令牌（预留，当前等价于 JWT）
        """
        auth_token = entity.get('auth_token', '')
        if not auth_token:
            return {'hasn_id': hasn_id, 'reason': '缺少 auth_token'}

        if not hasn_id.startswith('h_'):
            return {'hasn_id': hasn_id, 'reason': 'Human hasn_id 必须以 h_ 开头'}

        # 验证 auth_token
        try:
            if auth_token.startswith('hasn_ot_'):
                # Owner Token 验证（v5.0 预留）
                # 当前阶段：查询 DB 确认 hasn_id 存在 + 活跃
                from backend.app.hasn.model import HasnHumans
                from backend.database.db import async_db_session

                async with async_db_session() as db:
                    result = await db.execute(
                        select(HasnHumans).where(
                            HasnHumans.hasn_id == hasn_id,
                            HasnHumans.status == 'active',
                        )
                    )
                    human = result.scalar_one_or_none()
                    if not human:
                        return {'hasn_id': hasn_id, 'reason': 'Human 不存在或已停用'}
            else:
                # JWT Bearer Token 验证
                from backend.common.security.jwt import jwt_authentication
                user_info = await jwt_authentication(auth_token)

                # 校验 JWT 用户与 hasn_id 的对应关系
                from backend.app.hasn.model import HasnHumans
                from backend.database.db import async_db_session

                async with async_db_session() as db:
                    result = await db.execute(
                        select(HasnHumans).where(
                            HasnHumans.hasn_id == hasn_id,
                            HasnHumans.user_id == user_info.id,
                        )
                    )
                    human = result.scalar_one_or_none()
                    if not human:
                        return {'hasn_id': hasn_id, 'reason': 'auth_token 与 hasn_id 不匹配'}
        except Exception as e:
            return {'hasn_id': hasn_id, 'reason': f'auth_token 验证失败: {e}'}

        return None

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

    # ─── 动态实体管理（增量变更） ───

    async def add_entity(
        self,
        node_id: str,
        entity: dict,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """动态新增实体（hasn.node.add_entity）"""
        hasn_id = entity.get('hasn_id', '')
        entity_type = entity.get('entity_type', '')

        if entity_type == 'human':
            err = await self._validate_human(hasn_id, entity)
            if err:
                return {'hasn_id': hasn_id, 'accepted': False, 'reason': err['reason']}
            await self._register_entity(node_id, hasn_id, is_human=True)
            return {'hasn_id': hasn_id, 'accepted': True}

        elif entity_type == 'agent':
            err = await self._validate_agent(node_id, hasn_id, entity, db)
            if err:
                return {'hasn_id': hasn_id, 'accepted': False, 'reason': err['reason']}
            await self._register_entity(node_id, hasn_id, is_human=False)
            return {'hasn_id': hasn_id, 'accepted': True}

        return {'hasn_id': hasn_id, 'accepted': False, 'reason': f'未知 entity_type: {entity_type}'}

    async def remove_entity(self, node_id: str, hasn_id: str) -> None:
        """动态移除实体（hasn.node.remove_entity）"""
        existing = await redis_client.hget(ENTITY_NODE_KEY, hasn_id)
        if existing == node_id:
            await redis_client.hdel(ENTITY_NODE_KEY, hasn_id)
            await redis_client.srem(f'{NODE_ENTITIES_PREFIX}:{node_id}', hasn_id)
            if hasn_id.startswith('h_'):
                await redis_client.srem(f'{USER_NODES_PREFIX}:{hasn_id}', node_id)

    # 兼容旧接口
    async def report_agents(self, node_id, user_hasn_id, agents, db):
        entities = []
        entities.append({'hasn_id': user_hasn_id, 'entity_type': 'human', 'auth_token': 'legacy'})
        for a in agents:
            entities.append({
                'hasn_id': a.get('hasn_id', ''),
                'entity_type': 'agent',
                'owner_id': a.get('owner_id', user_hasn_id),
            })
        return await self.report_entities(node_id, entities, db)

    async def add_agent(self, node_id, user_hasn_id, hasn_id, db):
        return await self.add_entity(node_id, {
            'hasn_id': hasn_id, 'entity_type': 'agent', 'owner_id': user_hasn_id,
        }, db)

    async def remove_agent(self, node_id, hasn_id):
        await self.remove_entity(node_id, hasn_id)

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
