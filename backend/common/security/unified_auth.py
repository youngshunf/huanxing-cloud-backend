"""
统一认证中间件和 Scope 校验

支持 User JWT 和 Agent JWT 的统一认证入口。
根据 token_type 字段区分身份类型，并提供 Scope 校验装饰器。

@author Ysf
@date 2026-05-13
"""
from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param

from backend.common.dataclasses import AgentTokenPayload, TokenPayload
from backend.common.exception import errors
from backend.common.security.agent_jwt import verify_agent_token
from backend.common.security.jwt import jwt_authentication, jwt_decode


class TokenIdentity:
    """Token 身份基类"""
    pass


class UserIdentity(TokenIdentity):
    """用户身份"""
    def __init__(self, user_id: int, session_uuid: str):
        self.user_id = user_id
        self.session_uuid = session_uuid
        self.token_type = "user"


class AgentIdentity(TokenIdentity):
    """Agent 身份"""
    def __init__(
        self,
        agent_hasn_id: str,
        agent_name: str,
        owner_hasn_id: str,
        owner_user_id: int,
        scopes: list[str],
        session_uuid: str,
    ):
        self.agent_hasn_id = agent_hasn_id
        self.agent_name = agent_name
        self.owner_hasn_id = owner_hasn_id
        self.owner_user_id = owner_user_id
        self.scopes = scopes
        self.session_uuid = session_uuid
        self.token_type = "agent"

    def has_scope(self, scope: str) -> bool:
        """检查是否拥有指定权限"""
        return scope in self.scopes


def extract_bearer_token(request: Request) -> str | None:
    """
    从请求中提取 Bearer Token

    :param request: FastAPI 请求对象
    :return: Token 字符串或 None
    """
    authorization = request.headers.get('Authorization')
    if not authorization:
        return None

    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != 'bearer':
        return None

    return token


async def unified_jwt_auth(request: Request) -> TokenIdentity:
    """
    统一 JWT 认证：根据 token_type 分流到 User 或 Agent 逻辑

    :param request: FastAPI 请求对象
    :return: UserIdentity 或 AgentIdentity
    :raises HTTPException: 认证失败时抛出 401
    """
    token = extract_bearer_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证 Token")

    try:
        # 先尝试解析 token 判断类型
        from jose import jwt
        from backend.core.conf import settings

        payload = jwt.decode(
            token,
            settings.TOKEN_SECRET_KEY,
            algorithms=[settings.TOKEN_ALGORITHM],
            options={'verify_exp': False},  # 暂时不验证过期，让后续逻辑处理
        )

        token_type = payload.get('token_type', 'user')

        if token_type == 'agent':
            # Agent JWT 认证
            agent_payload = await verify_agent_token(token)
            identity = AgentIdentity(
                agent_hasn_id=agent_payload.agent_hasn_id,
                agent_name=agent_payload.agent_name,
                owner_hasn_id=agent_payload.owner_hasn_id,
                owner_user_id=agent_payload.owner_user_id,
                scopes=agent_payload.scopes,
                session_uuid=agent_payload.session_uuid,
            )
            # 注入到 request.state
            request.state.identity = identity
            request.state.agent_identity = identity
            return identity
        else:
            # User JWT 认证
            user = await jwt_authentication(token)
            identity = UserIdentity(
                user_id=user.id,
                session_uuid=payload.get('session_uuid', ''),
            )
            # 注入到 request.state
            request.state.identity = identity
            request.state.user = user
            return identity

    except errors.TokenError as e:
        raise HTTPException(status_code=401, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token 认证失败: {str(e)}")


def require_scope(scope: str):
    """
    路由级别的 scope 校验装饰器

    用法::

        @router.post("/posts")
        @require_scope("community.post")
        async def create_post(request: Request, identity: TokenIdentity = Depends(unified_jwt_auth)):
            ...

    :param scope: 需要的权限标识，如 "community.post"
    :return: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从 kwargs 中获取 identity 或 request
            identity = kwargs.get('identity')
            request = kwargs.get('request')

            # 如果没有 identity，尝试从 request.state 获取
            if not identity and request:
                identity = getattr(request.state, 'identity', None)

            if not identity:
                raise HTTPException(status_code=401, detail="未找到认证身份")

            # 只对 Agent 身份校验 scope
            if isinstance(identity, AgentIdentity):
                if not identity.has_scope(scope):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent 缺少权限: {scope}"
                    )

            # User 身份默认拥有所有权限，直接通过
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_scopes(*scopes: str):
    """
    路由级别的多 scope 校验装饰器（需要同时拥有所有权限）

    用法::

        @router.post("/posts")
        @require_scopes("community.post", "community.read")
        async def create_post(request: Request, identity: TokenIdentity = Depends(unified_jwt_auth)):
            ...

    :param scopes: 需要的权限标识列表
    :return: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            identity = kwargs.get('identity')
            request = kwargs.get('request')

            if not identity and request:
                identity = getattr(request.state, 'identity', None)

            if not identity:
                raise HTTPException(status_code=401, detail="未找到认证身份")

            if isinstance(identity, AgentIdentity):
                missing_scopes = [s for s in scopes if not identity.has_scope(s)]
                if missing_scopes:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Agent 缺少权限: {', '.join(missing_scopes)}"
                    )

            return await func(*args, **kwargs)

        return wrapper
    return decorator
