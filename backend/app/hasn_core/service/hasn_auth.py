"""
HASN JWT 签发 & API Key 验证 & FastAPI 认证依赖
对应设计文档: 07-API设计.md §一 认证机制
"""
import hashlib
from datetime import timedelta
from typing import Any

from fastapi import Depends, HTTPException, Request
from jose import ExpiredSignatureError, JWTError, jwt

from backend.common.log import log
from backend.core.conf import settings
from backend.database.db import async_db_session
from backend.app.hasn_core.crud.crud_agent import crud_hasn_agent


# ══════════════════════════════════════
# JWT 签发 / 验证
# ══════════════════════════════════════

def hasn_create_jwt(
    hasn_id: str,
    star_id: str,
    entity_type: str,
    expires_hours: int = 24,
) -> str:
    """
    签发 HASN 专用 JWT

    :param hasn_id: h_xxx 或 a_xxx
    :param star_id: 唤星号
    :param entity_type: "human" 或 "agent"
    :param expires_hours: 过期小时数，默认24
    :return: JWT token 字符串
    """
    from backend.utils.timezone import timezone

    now = timezone.now()
    payload = {
        'sub': hasn_id,
        'star_id': star_id,
        'type': entity_type,
        'iss': 'hasn',
        'iat': now,
        'exp': now + timedelta(hours=expires_hours),
    }
    return jwt.encode(payload, settings.TOKEN_SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)


def hasn_verify_jwt(token: str) -> dict[str, Any]:
    """
    验证 HASN JWT，返回解码后的 payload

    :param token: JWT token
    :return: {hasn_id, star_id, type}
    :raises HTTPException: token 无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.TOKEN_SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
            options={'verify_exp': True},
        )
        hasn_id = payload.get('sub')
        star_id = payload.get('star_id')
        entity_type = payload.get('type')
        if not hasn_id or not star_id or not entity_type:
            raise HTTPException(status_code=401, detail='HASN Token 无效: 缺少必要字段')
        return {
            'hasn_id': hasn_id,
            'star_id': star_id,
            'type': entity_type,
        }
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='HASN Token 已过期')
    except JWTError:
        raise HTTPException(status_code=401, detail='HASN Token 无效')


# ══════════════════════════════════════
# API Key 验证
# ══════════════════════════════════════

async def hasn_verify_api_key(api_key: str) -> dict[str, Any]:
    """
    验证 Agent API Key

    :param api_key: 明文 API Key (hasn_ak_xxx)
    :return: {hasn_id, star_id, type: "agent", owner_id}
    :raises HTTPException: key 无效
    """
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    async with async_db_session() as db:
        agent = await crud_hasn_agent.get_by_api_key_hash(db, key_hash)

    if not agent:
        raise HTTPException(status_code=401, detail='HASN API Key 无效')

    if agent.status != 'active':
        raise HTTPException(status_code=403, detail=f'Agent 状态异常: {agent.status}')

    return {
        'hasn_id': agent.id,
        'star_id': agent.star_id,
        'type': 'agent',
        'owner_id': agent.owner_id,
    }


# ══════════════════════════════════════
# FastAPI 统一认证依赖
# ══════════════════════════════════════

async def hasn_auth(request: Request) -> dict[str, Any]:
    """
    统一认证依赖 — Bearer JWT 或 ApiKey 双模式

    用法::

        @router.get("/xxx")
        async def xxx(auth: dict = Depends(hasn_auth)):
            hasn_id = auth["hasn_id"]
            star_id = auth["star_id"]
            entity_type = auth["type"]  # "human" 或 "agent"

    :return: {hasn_id, star_id, type}
    """
    auth_header = request.headers.get('Authorization', '')

    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
        if not token:
            raise HTTPException(status_code=401, detail='Bearer token 为空')
        result = hasn_verify_jwt(token)
        # Human 的 effective_id 就是自己
        result['effective_id'] = result['hasn_id']
        return result

    elif auth_header.startswith('ApiKey '):
        api_key = auth_header[7:].strip()
        if not api_key:
            raise HTTPException(status_code=401, detail='API Key 为空')
        result = await hasn_verify_api_key(api_key)
        # Agent 代表其 owner 行事，社交关系查 owner_id
        result['effective_id'] = result.get('owner_id', result['hasn_id'])
        return result

    else:
        raise HTTPException(
            status_code=401,
            detail='未提供认证信息。需要 Authorization: Bearer <jwt> 或 Authorization: ApiKey <key>',
        )
