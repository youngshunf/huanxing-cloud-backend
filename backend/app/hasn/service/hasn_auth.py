"""HASN 认证服务

提供 HASN 网络的认证能力：
- Human JWT 认证（复用平台 JWT）
- Client JWT 签发/验证（含 client_id）
- Agent API Key 认证
- HASN 身份注册（Human + 默认 Agent）
- Star ID 生成
"""

import hashlib
import secrets
import uuid
from datetime import timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.security.jwt import jwt_decode, jwt_authentication
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.database.redis import redis_client
from backend.utils.timezone import timezone

from backend.app.hasn.model import HasnHumans
from backend.app.hasn.model.hasn_agents import HasnAgents
from backend.app.hasn.model.hasn_clients import HasnClients


# ─── Star ID 生成 ───

async def _next_star_id(db: AsyncSession) -> str:
    """生成下一个数字唤星号（6位起步）"""
    result = await db.execute(
        select(HasnHumans.star_id)
        .where(HasnHumans.star_id.regexp_match(r'^\d+$'))
        .order_by(HasnHumans.id.desc())
        .limit(1)
    )
    last = result.scalar()
    if last:
        return str(int(last) + 1)
    return '100001'


def _generate_api_key() -> tuple[str, str]:
    """生成 Agent API Key 和对应的 SHA256 哈希"""
    raw_key = f"hasn_ak_{secrets.token_urlsafe(48)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


# ─── Client JWT ───

HASN_CLIENT_JWT_SECRET = settings.TOKEN_SECRET_KEY
HASN_CLIENT_JWT_ALGORITHM = 'HS256'
HASN_CLIENT_JWT_EXPIRE_SECONDS = 60 * 60 * 24  # 24 小时


def issue_client_jwt(
    user_hasn_id: str,
    client_id: str,
    client_type: str,
    star_id: str,
) -> str:
    """签发 Client JWT（用于 WebSocket 连接认证）"""
    now = timezone.now()
    expire = now + timedelta(seconds=HASN_CLIENT_JWT_EXPIRE_SECONDS)
    payload = {
        'sub': user_hasn_id,
        'client_id': client_id,
        'client_type': client_type,
        'star_id': star_id,
        'type': 'client',
        'iss': 'hasn',
        'iat': int(now.timestamp()),
        'exp': int(expire.timestamp()),
    }
    return jwt.encode(payload, HASN_CLIENT_JWT_SECRET, algorithm=HASN_CLIENT_JWT_ALGORITHM)


def verify_client_jwt(token: str) -> dict[str, Any]:
    """验证 Client JWT，返回 payload"""
    try:
        payload = jwt.decode(
            token,
            HASN_CLIENT_JWT_SECRET,
            algorithms=[HASN_CLIENT_JWT_ALGORITHM],
            options={'verify_exp': True},
        )
        if payload.get('type') != 'client':
            raise HTTPException(status_code=401, detail='非 Client JWT')
        # 补充统一节点字段（兼容旧 JWT）
        if 'node_id' not in payload:
            payload['node_id'] = payload.get('client_id', '')
        if 'node_type' not in payload:
            payload['node_type'] = payload.get('client_type', 'desktop')
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Client JWT 已过期')
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f'Client JWT 无效: {e}')


# ─── Node API Key 验证（统一节点模型） ───

async def verify_node_api_key(api_key: str) -> dict[str, Any]:
    """
    验证节点 API Key，返回节点身份信息。

    API Key 格式: hasn_ak_{64字符随机字符串}
    通过 hasn_clients 表中的 api_key_hash 查找对应节点记录。
    """
    if not api_key.startswith('hasn_ak_'):
        raise HTTPException(status_code=401, detail='无效的 API Key 格式')

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    async with async_db_session() as db:
        result = await db.execute(
            select(HasnClients).where(
                HasnClients.api_key_hash == key_hash,
                HasnClients.status == 'active',
            )
        )
        client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=401, detail='Node API Key 无效或节点已停用')

    return {
        'sub': client.user_hasn_id,
        'node_id': client.client_id,
        'node_type': client.client_type,
        'capacity': getattr(client, 'capacity', 1) or 1,
        'star_id': '',
        'type': 'node_api_key',
    }


# ─── Agent API Key 验证 ───

async def verify_agent_api_key(api_key: str, db: AsyncSession) -> HasnAgents:
    """验证 Agent API Key，返回 Agent 记录"""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    result = await db.execute(
        select(HasnAgents).where(
            HasnAgents.api_key_hash == key_hash,
            HasnAgents.status == 'active',
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=401, detail='Agent API Key 无效或 Agent 已停用')
    return agent


# ─── HASN 身份注册 ───

async def register_hasn_identity(
    db: AsyncSession,
    user_id: int,
    name: str,
    avatar_url: str | None = None,
    bio: str | None = None,
) -> dict[str, Any]:
    """
    为平台用户注册 HASN 身份（Human + 默认 Agent）

    幂等：若用户已注册，返回已有记录。

    返回: {human: HasnHumans, agent: HasnAgents, api_key: str | None, already_exists: bool}
    """
    # 幂等检查：已注册则直接返回
    result = await db.execute(
        select(HasnHumans).where(HasnHumans.user_id == user_id)
    )
    existing_human = result.scalar_one_or_none()
    if existing_human:
        # 查找其默认 Agent
        agent_result = await db.execute(
            select(HasnAgents).where(
                HasnAgents.owner_id == existing_human.hasn_id,
            ).order_by(HasnAgents.id.asc()).limit(1)
        )
        existing_agent = agent_result.scalar_one_or_none()
        return {
            'human': existing_human,
            'agent': existing_agent,
            'api_key': None,  # 已注册不返回 api_key（安全）
            'already_exists': True,
        }

    # 生成 HASN ID 和 Star ID
    hasn_id = f"h_{uuid.uuid4()}"
    star_id = await _next_star_id(db)

    # 创建 Human
    human = HasnHumans(
        hasn_id=hasn_id,
        star_id=star_id,
        user_id=user_id,
        name=name,
        bio=bio,
        avatar_url=avatar_url,
        status='active',
        contact_policy={
            'human_direct': 'open',
            'via_agent': 'allowed',
            'stranger_policy': 'agent_screens_first',
            'commerce_policy': 'discovery_only',
            'service_policy': 'order_auto_create',
            'professional_policy': 'discovery_then_approve',
        },
        stats={'contacts_count': 0, 'agents_count': 0},
    )
    db.add(human)
    await db.flush()

    # 注意：不再自动创建默认 Agent
    # Agent 由客户端按需注册（local 或 cloud），避免创建未部署的幽灵 Agent

    return {
        'human': human,
        'agent': None,
        'api_key': None,
        'already_exists': False,
    }


async def register_hasn_agent(
    db: AsyncSession,
    owner_hasn_id: str,
    agent_name: str,
    display_name: str,
    agent_type: str = 'local',
    server_id: str | None = None,
    home_client_id: int | None = None,
    created_via: str = 'client',
) -> dict[str, Any]:
    """
    为已有 Human 注册新 Agent 的 HASN 身份

    幂等：同一 owner + agent_name 不重复创建

    返回: {agent: HasnAgents, api_key: str | None, already_exists: bool}
    """
    # 验证 owner 存在
    owner_result = await db.execute(
        select(HasnHumans).where(HasnHumans.hasn_id == owner_hasn_id)
    )
    owner = owner_result.scalar_one_or_none()
    if not owner:
        raise HTTPException(status_code=404, detail='owner_hasn_id 对应的 Human 不存在')

    # 幂等检查
    existing_result = await db.execute(
        select(HasnAgents).where(
            HasnAgents.owner_id == owner_hasn_id,
            HasnAgents.agent_name == agent_name,
        )
    )
    existing_agent = existing_result.scalar_one_or_none()
    if existing_agent:
        return {
            'agent': existing_agent,
            'api_key': None,
            'already_exists': True,
        }

    # 生成身份
    agent_hasn_id = f"a_{uuid.uuid4()}"
    agent_star_id = f"{owner.star_id}#{agent_name}"
    api_key, api_key_hash = _generate_api_key()

    agent = HasnAgents(
        hasn_id=agent_hasn_id,
        star_id=agent_star_id,
        owner_id=owner_hasn_id,
        name=display_name,
        agent_name=agent_name,
        type=agent_type,
        server_id=server_id,
        home_client_id=home_client_id,
        api_key_hash=api_key_hash,
        status='active',
        created_via=created_via,
    )
    db.add(agent)
    await db.flush()

    return {
        'agent': agent,
        'api_key': api_key,
        'already_exists': False,
    }


# ─── 客户端注册 ───

async def register_client(
    db: AsyncSession,
    user_hasn_id: str,
    client_type: str,
    device_name: str | None = None,
    device_info: dict | None = None,
) -> HasnClients:
    """注册客户端设备（幂等：相同 user + device_fingerprint 不重复创建）"""
    # 幂等检查：如果 device_info 中有 device_fingerprint，查找已有客户端
    fingerprint = (device_info or {}).get('device_fingerprint')
    if fingerprint:
        result = await db.execute(
            select(HasnClients).where(
                HasnClients.user_hasn_id == user_hasn_id,
                HasnClients.status == 'active',
                HasnClients.device_info['device_fingerprint'].astext == fingerprint,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            # 更新最后活跃时间
            existing.last_seen_at = timezone.now()
            if device_name and existing.device_name != device_name:
                existing.device_name = device_name
            await db.flush()
            return existing

    client_id = f"c_{uuid.uuid4().hex[:12]}"

    client = HasnClients(
        client_id=client_id,
        user_hasn_id=user_hasn_id,
        client_type=client_type,
        device_name=device_name,
        device_info=device_info or {},
        status='active',
    )
    db.add(client)
    await db.flush()
    return client


# ─── 认证依赖注入 ───

async def hasn_auth_from_jwt(request: Request) -> dict[str, Any]:
    """
    从平台 JWT 中提取 HASN 身份

    用于 REST API 认证，返回:
    {
        "hasn_id": "h_xxx",
        "star_id": "100001",
        "user_id": 123,
        "auth_type": "jwt"
    }
    """
    authorization = request.headers.get('Authorization')
    if not authorization:
        raise HTTPException(status_code=401, detail='缺少认证信息')

    scheme, credentials = get_authorization_scheme_param(authorization)
    if scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail='仅支持 Bearer 认证')

    # 验证平台 JWT
    user_info = await jwt_authentication(credentials)
    user_id = user_info.id

    # 查找 HASN 身份
    async with async_db_session() as db:
        result = await db.execute(
            select(HasnHumans).where(HasnHumans.user_id == user_id)
        )
        human = result.scalar_one_or_none()

    if not human:
        raise HTTPException(status_code=404, detail='未注册 HASN 身份，请先注册')

    return {
        'hasn_id': human.hasn_id,
        'star_id': human.star_id,
        'user_id': user_id,
        'name': human.name,
        'auth_type': 'jwt',
    }


async def hasn_auth_dual(request: Request) -> dict[str, Any]:
    """
    HASN 双模式认证：Bearer JWT 或 ApiKey

    返回:
    {
        "hasn_id": "h_xxx" 或 "a_xxx",
        "star_id": "100001" 或 "100001#star",
        "entity_type": "human" 或 "agent",
        "auth_type": "jwt" 或 "apikey"
    }
    """
    authorization = request.headers.get('Authorization')
    if not authorization:
        raise HTTPException(status_code=401, detail='缺少认证信息')

    scheme, credentials = get_authorization_scheme_param(authorization)

    if scheme.lower() == 'bearer':
        return await hasn_auth_from_jwt(request)

    elif scheme.lower() == 'apikey':
        async with async_db_session() as db:
            agent = await verify_agent_api_key(credentials, db)
        return {
            'hasn_id': agent.hasn_id,
            'star_id': agent.star_id,
            'entity_type': 'agent',
            'owner_id': agent.owner_id,
            'auth_type': 'apikey',
        }

    else:
        raise HTTPException(status_code=401, detail=f'不支持的认证方式: {scheme}')


# 依赖注入快捷方式
DependsHasnAuth = Depends(hasn_auth_from_jwt)
DependsHasnDualAuth = Depends(hasn_auth_dual)

# 兼容别名（contacts.py 使用此名称）
hasn_auth = hasn_auth_from_jwt
