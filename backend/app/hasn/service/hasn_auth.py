"""HASN 认证服务.

提供 HASN 网络的认证能力：
- Human JWT 认证（复用平台 JWT）
- Node JWT 签发/验证（可选能力）
- Node Key 认证
- Owner API Key 认证
- Agent API Key 认证
- HASN 身份注册
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

from backend.app.hasn.model import HasnHumans, HasnNodes, HasnOwnerApiKeys
from backend.app.hasn.model.hasn_agents import HasnAgents


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


def _generate_agent_key() -> tuple[str, str]:
    """生成 Agent Key (hasn_ak_) 和对应的 SHA256 哈希"""
    raw_key = f"hasn_ak_{secrets.token_urlsafe(48)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


def _generate_node_key() -> tuple[str, str]:
    """生成 Node Key (hasn_nk_ 前缀) 和对应的 SHA256 哈希"""
    raw_key = f"hasn_nk_{secrets.token_urlsafe(48)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


def _generate_owner_key() -> tuple[str, str]:
    """生成 Owner API Key (hasn_ok_) 和对应的 SHA256 哈希"""
    raw_key = f"hasn_ok_{secrets.token_urlsafe(48)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


# ─── Node JWT ───

HASN_CLIENT_JWT_SECRET = settings.TOKEN_SECRET_KEY
HASN_CLIENT_JWT_ALGORITHM = 'HS256'
HASN_CLIENT_JWT_EXPIRE_SECONDS = 60 * 60 * 24  # 24 小时


def issue_node_jwt(
    user_hasn_id: str,
    node_id: str,
    node_type: str,
    star_id: str,
) -> str:
    """签发 Node JWT（可选能力）"""
    now = timezone.now()
    expire = now + timedelta(seconds=HASN_CLIENT_JWT_EXPIRE_SECONDS)
    payload = {
        'sub': user_hasn_id,
        'node_id': node_id,
        'node_type': node_type,
        'star_id': star_id,
        'type': 'node',
        'iss': 'hasn',
        'iat': int(now.timestamp()),
        'exp': int(expire.timestamp()),
    }
    return jwt.encode(payload, HASN_CLIENT_JWT_SECRET, algorithm=HASN_CLIENT_JWT_ALGORITHM)


def verify_node_jwt(token: str) -> dict[str, Any]:
    """验证 Node JWT，返回 payload"""
    try:
        payload = jwt.decode(
            token,
            HASN_CLIENT_JWT_SECRET,
            algorithms=[HASN_CLIENT_JWT_ALGORITHM],
            options={'verify_exp': True},
        )
        if payload.get('type') != 'node':
            raise HTTPException(status_code=401, detail='非 Node JWT')
        if 'node_id' not in payload:
            raise HTTPException(status_code=401, detail='Node JWT 缺少 node_id')
        if 'node_type' not in payload:
            payload['node_type'] = 'desktop'
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Node JWT 已过期')
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f'Node JWT 无效: {e}')


# ─── Node Key 验证（统一节点模型 v5.0） ───

async def verify_node_key(node_key: str) -> dict[str, Any]:
    """
    验证节点 Node Key，返回节点身份信息（不包含用户身份）。

    Node Key 格式: hasn_nk_{64字符随机字符串}
    Node Key 仅验证物理节点合法性，不绑定任何用户身份。
    用户身份通过后续的 Owner Binding / Agent Presence 建立。
    """
    if not node_key.startswith('hasn_nk_'):
        raise HTTPException(status_code=401, detail='无效的 Node Key 格式（期望 hasn_nk_ 前缀）')

    key_hash = hashlib.sha256(node_key.encode()).hexdigest()

    async with async_db_session() as db:
        result = await db.execute(
            select(HasnNodes).where(
                HasnNodes.node_key_hash == key_hash,
                HasnNodes.status == 'active',
            )
        )
        node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(status_code=401, detail='Node Key 无效或节点已停用')

    return {
        'node_id': node.node_id,
        'node_type': node.node_type,
        'capacity': getattr(node, 'capacity', 1) or 1,
        'type': 'node_key',
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


async def verify_owner_api_key(owner_hasn_id: str, owner_api_key: str, db: AsyncSession) -> HasnOwnerApiKeys:
    """验证 Owner API Key，返回 Key 记录"""
    key_hash = hashlib.sha256(owner_api_key.encode()).hexdigest()
    result = await db.execute(
        select(HasnOwnerApiKeys).where(
            HasnOwnerApiKeys.owner_id == owner_hasn_id,
            HasnOwnerApiKeys.key_hash == key_hash,
            HasnOwnerApiKeys.status == 'active',
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=401, detail='Owner API Key 无效或已停用')
    return key


async def verify_owner_proof(
    owner_id: str,
    owner_proof: dict[str, Any],
    node_id: str | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """验证 Owner Proof，返回标准化结果。"""
    proof_type = owner_proof.get('type', '')
    credential = owner_proof.get('credential', '')
    if not proof_type or not credential:
        raise HTTPException(status_code=401, detail='缺少 owner_proof')

    now = timezone.now()

    if node_id:
        node_result = await db.execute(
            select(HasnNodes).where(
                HasnNodes.node_id == node_id,
                HasnNodes.status == 'active',
            )
        )
        node = node_result.scalar_one_or_none()
        if not node:
            raise HTTPException(status_code=401, detail='Node 不存在或已停用')
        allowed_owner_hasn_ids = node.allowed_owner_hasn_ids or []
        if allowed_owner_hasn_ids and owner_id not in allowed_owner_hasn_ids:
            raise HTTPException(status_code=403, detail='当前 Node 不允许绑定该 Owner')

    if proof_type == 'owner_api_key':
        # 复用公共 owner key 验证（已含过期检查 + last_used 更新）
        from backend.common.security.owner_key_auth import verify_owner_key_standalone
        key = await verify_owner_key_standalone(credential, db)
        # 额外校验：owner_id 必须匹配
        if key.owner_id != owner_id:
            raise HTTPException(status_code=401, detail='Owner API Key 与 owner_id 不匹配')
        if key.bound_node_id and node_id and key.bound_node_id != node_id:
            raise HTTPException(status_code=401, detail='Owner API Key 与当前 Node 不匹配')
        return {
            'auth_profile': 'owner_api_key',
            'scopes': key.scopes or {'bind_owner': True, 'register_agent': True},
            'expires_at': key.expires_at,
            'key_id': key.key_id,
        }

    if proof_type == 'bearer_token':
        user_info = await jwt_authentication(credential)
        result = await db.execute(
            select(HasnHumans).where(
                HasnHumans.hasn_id == owner_id,
                HasnHumans.user_id == user_info.id,
            )
        )
        human = result.scalar_one_or_none()
        if not human:
            raise HTTPException(status_code=401, detail='Bearer Token 与 owner_id 不匹配')
        token_payload = jwt_decode(credential)
        # default to 7 days lease for bearer token
        expires_at = timezone.now() + timedelta(days=7)
        return {
            'auth_profile': 'bearer_token',
            'scopes': {'bind_owner': True, 'register_agent': True},
            'expires_at': expires_at,
            'key_id': None,
        }

    raise HTTPException(status_code=401, detail=f'不支持的 owner_proof.type: {proof_type}')


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
    agent_type: str = 'desktop',
    node_id: str | None = None,
    role: str = 'specialist',
    description: str | None = None,
    capabilities: list | None = None,
    created_via: str = 'client',
    avatar_url: str | None = None,
) -> dict[str, Any]:
    """
    为已有 Human 注册新 Agent 的 HASN 身份

    幂等：同一 owner + agent_name 不重复创建

    参数:
      agent_type: desktop | mobile | cloud | web
      node_id: Agent 驻留节点 ID（设备指纹派生）
      role: primary | specialist | service
      description: Agent 描述
      capabilities: A2A AgentCard 兼容能力列表
      avatar_url: CDN 头像 URL

    返回: {agent: HasnAgents, agent_key: str | None, already_exists: bool}
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
        # 幂等更新：如果属性变了，更新记录
        updated = False
        if node_id and existing_agent.node_id != node_id:
            existing_agent.node_id = node_id
            updated = True
        if display_name and existing_agent.name != display_name:
            existing_agent.name = display_name
            updated = True
        if agent_type and existing_agent.type != agent_type:
            existing_agent.type = agent_type
            updated = True
        if avatar_url and existing_agent.avatar_url != avatar_url:
            existing_agent.avatar_url = avatar_url
            updated = True
        if updated:
            await db.flush()
        return {
            'agent': existing_agent,
            'agent_key': None,
            'already_exists': True,
        }

    # 生成身份
    agent_hasn_id = f"a_{uuid.uuid4()}"
    agent_star_id = f"{owner.star_id}#{agent_name}"
    agent_key, agent_key_hash = _generate_agent_key()

    agent = HasnAgents(
        hasn_id=agent_hasn_id,
        star_id=agent_star_id,
        owner_id=owner_hasn_id,
        name=display_name,
        agent_name=agent_name,
        type=agent_type,
        node_id=node_id,
        role=role or 'specialist',
        description=description,
        capabilities=capabilities,
        avatar_url=avatar_url,
        api_key_hash=agent_key_hash,
        status='active',
        created_via=created_via,
    )
    db.add(agent)
    await db.flush()

    return {
        'agent': agent,
        'agent_key': agent_key,
        'already_exists': False,
    }


# ─── 节点注册 ───

async def register_node(
    db: AsyncSession,
    user_id: int | None,
    owner_hasn_id: str,
    node_type: str,
    node_name: str | None = None,
    node_info: dict | None = None,
    allowed_owner_hasn_ids: list[str] | None = None,
) -> HasnNodes:
    """注册 Node（幂等：按 device_fingerprint 去重，同一物理设备永远只有一条记录）"""
    node_info = node_info or {}
    fingerprint = node_info.get('device_fingerprint')
    device_platform = node_info.get('device_platform') or node_info.get('platform')
    app_version = node_info.get('app_version')
    capacity = int(node_info.get('capacity') or (3 if node_type == 'desktop' else 1))
    created_by_owner_id = owner_hasn_id

    # 幂等检查：按 device_fingerprint 查找（不限 user_id，因为同一设备可能被不同用户登录）
    if fingerprint:
        result = await db.execute(
            select(HasnNodes).where(
                HasnNodes.device_fingerprint == fingerprint,
                HasnNodes.status == 'active',
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            # 更新可变字段
            existing.last_seen_at = timezone.now()
            existing.user_id = user_id or existing.user_id
            if node_name and existing.node_name != node_name:
                existing.node_name = node_name
            existing.node_type = node_type or existing.node_type
            existing.capacity = capacity or existing.capacity
            # 合并 allowed_owner_hasn_ids（多用户同设备）
            if owner_hasn_id:
                current_owners = existing.allowed_owner_hasn_ids or []
                if owner_hasn_id not in current_owners:
                    existing.allowed_owner_hasn_ids = current_owners + [owner_hasn_id]
            if allowed_owner_hasn_ids is not None:
                existing.allowed_owner_hasn_ids = allowed_owner_hasn_ids
            existing.created_by_owner_id = created_by_owner_id or existing.created_by_owner_id
            existing.device_platform = device_platform or existing.device_platform
            existing.app_version = app_version or existing.app_version
            existing.node_info = node_info or existing.node_info
            await db.flush()
            return existing

    # 新建节点：node_id 由设备指纹派生
    if fingerprint:
        node_id = f"n_{hashlib.sha256(fingerprint.encode()).hexdigest()[:16]}"
    else:
        node_id = f"n_{uuid.uuid4().hex[:12]}"

    node = HasnNodes(
        node_id=node_id,
        user_id=user_id,
        allowed_owner_hasn_ids=allowed_owner_hasn_ids or ([owner_hasn_id] if owner_hasn_id else None),
        node_type=node_type,
        node_name=node_name,
        device_fingerprint=fingerprint,
        device_platform=device_platform,
        app_version=app_version,
        node_info=node_info,
        created_by_owner_id=created_by_owner_id,
        capacity=capacity,
        status='active',
    )
    db.add(node)
    await db.flush()
    return node


# ─── 登录时自动 HASN 注册 + Node Key 签发 ───

async def ensure_hasn_node_key(
    db: AsyncSession,
    user_id: int,
    nickname: str,
    client_type: str = 'desktop',
    device_name: str | None = None,
    device_fingerprint: str | None = None,
) -> str | None:
    """
    登录时调用：确保 HASN 身份已注册 + 节点设备已注册 + 签发 Node Key

    幂等：同一设备（由 device_fingerprint 标识）永远复用同一条 hasn_nodes 记录。
    如果任何步骤失败，返回 None（不阻塞登录）。

    参数:
        device_fingerprint: 设备指纹（32字符 hex），由 ZeroClaw 进程在启动时派生。
                            缺失时退化为按 user_id 区分（每个用户每次登录创建新记录）。
        device_name: 节点名称，建议格式为 "macOS 14.4.1" / "Windows 11"。

    返回: node_key (hasn_nk_xxx) 或 None
    """
    from backend.common.log import log
    try:
        # 1. 注册 HASN Human（幂等）
        identity = await register_hasn_identity(
            db=db,
            user_id=user_id,
            name=nickname,
        )
        hasn_id = identity['human'].hasn_id

        # 2. 注册 Node 设备（幂等：device_fingerprint 是去重 Key）
        node_info: dict = {
            'source': 'login_auto',
            'client_type': client_type,
            'device_platform': client_type,
        }
        if device_fingerprint:
            node_info['device_fingerprint'] = device_fingerprint

        node = await register_node(
            db=db,
            user_id=user_id,
            owner_hasn_id=hasn_id,
            node_type=client_type,
            node_name=device_name,
            node_info=node_info,
            allowed_owner_hasn_ids=None,
        )

        # 3. 签发新 Node Key（每次登录刷新；旧 key 自动失效，因为 hash 被覆盖）
        node_key, node_key_hash = _generate_node_key()
        node.node_key_hash = node_key_hash
        node.last_seen_at = timezone.now()
        await db.flush()

        log.info(f'[HASN] 登录自动注册 OK: user_id={user_id}, hasn_id={hasn_id}, '
                 f'node_id={node.node_id}, fingerprint={device_fingerprint or "N/A"}')
        return node_key

    except Exception as e:
        log.warning(f'[HASN] 登录自动注册 HASN 失败（不阻塞登录）: {e}')
        return None


async def ensure_hasn_owner_key(
    db: AsyncSession,
    user_id: int,
    nickname: str,
) -> str | None:
    """
    登录时调用：确保 Owner API Key 已签发（幂等）。

    - 已有 active key → 直接返回 None（明文只在首次创建时返回）
    - 没有 active key → 签发新 key，返回明文 hasn_ok_xxx
    - 失败 → 返回 None（不阻塞登录）

    返回: owner_key (hasn_ok_xxx) 或 None
    """
    from backend.common.log import log
    try:
        # 1. 确保 HASN Human 身份已注册
        identity = await register_hasn_identity(
            db=db,
            user_id=user_id,
            name=nickname,
        )
        hasn_id = identity['human'].hasn_id

        # 2. 检查是否已有 active 的 Owner Key
        existing = await db.execute(
            select(HasnOwnerApiKeys).where(
                HasnOwnerApiKeys.user_id == user_id,
                HasnOwnerApiKeys.status == 'active',
            ).limit(1)
        )
        if existing.scalar_one_or_none():
            log.debug(f'[HASN] Owner Key 已存在: user_id={user_id}')
            return None  # 已有 key，明文不可恢复

        # 3. 签发新 Owner Key
        from backend.app.hasn.service.hasn_api_key_service import hasn_api_key_service
        result = await hasn_api_key_service.create_api_key(
            db=db,
            user_id=user_id,
            user_hasn_id=hasn_id,
            name='Auto (login)',
            scopes={'bind_owner': True, 'register_agent': True},
        )
        log.info(f'[HASN] Owner Key 签发 OK: user_id={user_id}, key_id={result.key_id}')
        return result.owner_api_key

    except Exception as e:
        log.warning(f'[HASN] Owner Key 签发失败（不阻塞登录）: {e}')
        return None

async def reissue_hasn_node_key(
    db: AsyncSession,
    node_id: str,
    owner_hasn_id: str,
) -> str:
    """重新签发 Node Key，覆盖旧 hash，返回新明文。"""
    result = await db.execute(
        select(HasnNodes).where(
            HasnNodes.node_id == node_id,
            HasnNodes.status == 'active',
        )
    )
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail='Node 不存在或已停用')

    allowed = node.allowed_owner_hasn_ids or []
    if node.created_by_owner_id != owner_hasn_id and owner_hasn_id not in allowed:
        raise HTTPException(status_code=403, detail='无权为该 Node 重新签发 Node Key')

    node_key, node_key_hash = _generate_node_key()
    node.node_key_hash = node_key_hash
    node.last_seen_at = timezone.now()
    await db.flush()
    return node_key


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


async def hasn_auth_from_node_credential(request: Request) -> dict[str, Any]:
    """从 Authorization 中提取 Node 认证信息。"""
    authorization = request.headers.get('Authorization')
    if not authorization:
        raise HTTPException(status_code=401, detail='缺少认证信息')

    scheme, credentials = get_authorization_scheme_param(authorization)
    if scheme == 'NodeKey':
        return await verify_node_key(credentials)
    raise HTTPException(status_code=401, detail='仅支持 NodeKey 认证')


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
DependsHasnNodeAuth = Depends(hasn_auth_from_node_credential)

# 兼容别名（contacts.py 使用此名称）
hasn_auth = hasn_auth_from_jwt
