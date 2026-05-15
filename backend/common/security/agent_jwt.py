"""
Agent JWT 认证模块

Agent 使用独立的 JWT 进行身份认证，与 Owner JWT 平级但权限受限。
每个 Agent JWT 包含 scopes 字段，用于细粒度权限控制。

认证方式: Header `Authorization: Bearer <agent_jwt>`
Token Type: agent (通过 payload.token_type 区分)

@author Ysf
@date 2026-05-13
"""
import json
import uuid
from datetime import timedelta
from typing import Any

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.dataclasses import AgentAccessToken, AgentTokenPayload
from backend.common.exception import errors
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.timezone import timezone


# 默认 Agent Scopes（只读权限）
DEFAULT_AGENT_SCOPES = [
    "community.read",
    "message.read",
    "contact.read",
    "task.execute",
    "knowledge.read",
    "profile.read",
]


def jwt_encode_agent(payload: dict[str, Any]) -> str:
    """
    生成 Agent JWT token

    :param payload: 载荷
    :return: JWT token
    """
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)


def jwt_decode_agent(token: str) -> AgentTokenPayload:
    """
    解析 Agent JWT token

    :param token: JWT token
    :return: AgentTokenPayload
    """
    try:
        payload = jwt.decode(
            token,
            settings.TOKEN_SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
            options={'verify_exp': True},
        )

        token_type = payload.get('token_type')
        if token_type != 'agent':
            raise errors.TokenError(msg='Token 类型错误')

        agent_hasn_id = payload.get('agent_hasn_id')
        agent_name = payload.get('agent_name')
        owner_hasn_id = payload.get('owner_hasn_id')
        owner_user_id = payload.get('owner_user_id')
        scopes = payload.get('scopes', [])
        session_uuid = payload.get('session_uuid')
        expire = payload.get('exp')

        if not all([agent_hasn_id, owner_hasn_id, owner_user_id, session_uuid, expire]):
            raise errors.TokenError(msg='Agent Token 无效')

        return AgentTokenPayload(
            agent_hasn_id=agent_hasn_id,
            agent_name=agent_name or "",
            owner_hasn_id=owner_hasn_id,
            owner_user_id=int(owner_user_id),
            scopes=scopes,
            session_uuid=session_uuid,
            expire_time=timezone.from_datetime(timezone.to_utc(expire)),
            token_type='agent',
        )
    except errors.TokenError:
        raise
    except Exception as e:
        raise errors.TokenError(msg=f'Agent Token 解析失败: {str(e)}')


async def create_agent_access_token(
    agent_hasn_id: str,
    agent_name: str,
    owner_hasn_id: str,
    owner_user_id: int,
    scopes: list[str],
) -> AgentAccessToken:
    """
    生成 Agent JWT token

    :param agent_hasn_id: Agent 的 HASN ID
    :param agent_name: Agent 显示名
    :param owner_hasn_id: Owner 的 HASN ID
    :param owner_user_id: Owner 的 user_id
    :param scopes: 权限列表
    :return: AgentAccessToken
    """
    expire = timezone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
    session_uuid = str(uuid.uuid4())

    payload = {
        'sub': agent_hasn_id,
        'token_type': 'agent',
        'agent_hasn_id': agent_hasn_id,
        'agent_name': agent_name,
        'owner_hasn_id': owner_hasn_id,
        'owner_user_id': owner_user_id,
        'scopes': scopes,
        'session_uuid': session_uuid,
        'exp': timezone.to_utc(expire).timestamp(),
    }

    access_token = jwt_encode_agent(payload)

    # 存储到 Redis
    await redis_client.setex(
        f'agent_token:{agent_hasn_id}:{session_uuid}',
        settings.TOKEN_EXPIRE_SECONDS,
        access_token,
    )

    return AgentAccessToken(
        access_token=access_token,
        access_token_expire_time=expire,
        session_uuid=session_uuid,
        scopes=scopes,
    )


async def revoke_agent_token(agent_hasn_id: str, session_uuid: str) -> None:
    """
    吊销 Agent token

    :param agent_hasn_id: Agent 的 HASN ID
    :param session_uuid: 会话 UUID
    :return:
    """
    await redis_client.delete(f'agent_token:{agent_hasn_id}:{session_uuid}')


async def revoke_all_agent_tokens(agent_hasn_id: str) -> None:
    """
    吊销某个 Agent 的所有 token

    :param agent_hasn_id: Agent 的 HASN ID
    :return:
    """
    await redis_client.delete_prefix(f'agent_token:{agent_hasn_id}:')


async def verify_agent_token(token: str) -> AgentTokenPayload:
    """
    验证 Agent JWT token

    :param token: JWT token
    :return: AgentTokenPayload
    """
    token_payload = jwt_decode_agent(token)

    # 检查 Redis 中是否存在（支持主动吊销）
    redis_token = await redis_client.get(
        f'agent_token:{token_payload.agent_hasn_id}:{token_payload.session_uuid}'
    )

    if not redis_token:
        raise errors.TokenError(msg='Agent Token 已过期或已被吊销')

    if token != redis_token:
        raise errors.TokenError(msg='Agent Token 已失效')

    return token_payload


async def get_agent_scopes_from_db(db: AsyncSession, agent_hasn_id: str) -> dict[str, Any]:
    """
    从数据库查询 Agent 的权限配置

    :param db: 数据库会话
    :param agent_hasn_id: Agent 的 HASN ID
    :return: {"scopes": [...], "post_needs_review": bool}
    """
    from sqlalchemy import select, text

    # 查询 hasn_agent_scopes 表
    result = await db.execute(
        text("""
            SELECT scopes, post_needs_review
            FROM hasn_agent_scopes
            WHERE agent_hasn_id = :agent_hasn_id
        """),
        {"agent_hasn_id": agent_hasn_id}
    )
    row = result.fetchone()

    if not row:
        # 如果没有记录，返回默认权限
        return {
            "scopes": DEFAULT_AGENT_SCOPES,
            "post_needs_review": True,
        }

    return {
        "scopes": list(row[0]) if row[0] else DEFAULT_AGENT_SCOPES,
        "post_needs_review": row[1],
    }


async def get_agent_scopes_cached(agent_hasn_id: str, db: AsyncSession) -> dict[str, Any]:
    """
    获取 Agent 权限配置（带缓存）

    :param agent_hasn_id: Agent 的 HASN ID
    :param db: 数据库会话
    :return: {"scopes": [...], "post_needs_review": bool}
    """
    cache_key = f'agent_scopes:{agent_hasn_id}'

    # 尝试从 Redis 获取
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 从数据库查询
    scopes_config = await get_agent_scopes_from_db(db, agent_hasn_id)

    # 缓存 1 小时
    await redis_client.setex(
        cache_key,
        3600,
        json.dumps(scopes_config, ensure_ascii=False),
    )

    return scopes_config


async def invalidate_agent_scopes_cache(agent_hasn_id: str) -> None:
    """
    清除 Agent 权限缓存

    :param agent_hasn_id: Agent 的 HASN ID
    :return:
    """
    await redis_client.delete(f'agent_scopes:{agent_hasn_id}')


async def create_default_agent_scopes(db: AsyncSession, agent_hasn_id: str, owner_hasn_id: str) -> None:
    """
    为新创建的 Agent 插入默认权限配置

    :param db: 数据库会话
    :param agent_hasn_id: Agent 的 HASN ID
    :param owner_hasn_id: Owner 的 HASN ID
    :return:
    """
    from sqlalchemy import text

    await db.execute(
        text("""
            INSERT INTO hasn_agent_scopes (agent_hasn_id, owner_hasn_id, scopes, post_needs_review)
            VALUES (:agent_hasn_id, :owner_hasn_id, :scopes, :post_needs_review)
            ON CONFLICT (agent_hasn_id) DO NOTHING
        """),
        {
            "agent_hasn_id": agent_hasn_id,
            "owner_hasn_id": owner_hasn_id,
            "scopes": DEFAULT_AGENT_SCOPES,
            "post_needs_review": True,
        }
    )
    await db.commit()


async def update_agent_scopes(
    db: AsyncSession,
    agent_hasn_id: str,
    scopes: list[str],
    post_needs_review: bool,
    granted_by: str,
) -> None:
    """
    更新 Agent 权限配置

    :param db: 数据库会话
    :param agent_hasn_id: Agent 的 HASN ID
    :param scopes: 新的权限列表
    :param post_needs_review: 发帖是否需要审核
    :param granted_by: 授权者的 HASN ID
    :return:
    """
    from sqlalchemy import text

    # 更新数据库
    await db.execute(
        text("""
            UPDATE hasn_agent_scopes
            SET scopes = :scopes,
                post_needs_review = :post_needs_review,
                granted_by = :granted_by,
                granted_at = NOW()
            WHERE agent_hasn_id = :agent_hasn_id
        """),
        {
            "agent_hasn_id": agent_hasn_id,
            "scopes": scopes,
            "post_needs_review": post_needs_review,
            "granted_by": granted_by,
        }
    )
    await db.commit()

    # 删除缓存
    await invalidate_agent_scopes_cache(agent_hasn_id)

    # 吊销所有旧的 Agent JWT
    await revoke_all_agent_tokens(agent_hasn_id)
