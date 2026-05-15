"""
Agent JWT 认证依赖

Agent 使用独立的 JWT 进行身份认证，通过 Authorization header 传递。
支持细粒度的 Scope 权限控制。

认证方式: Header `Authorization: Bearer <agent_jwt>`
路由前缀: /api/v1/hasn/agent/

@author Ysf
@date 2026-05-13
"""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.common.dataclasses import AgentTokenPayload
from backend.common.exception import errors
from backend.common.log import log
from backend.common.security.agent_jwt import verify_agent_token
from backend.database.db import CurrentSession

# Bearer token 提取器
_bearer_scheme = HTTPBearer(auto_error=False)


async def agent_jwt_auth(
    request: Request,
    db: CurrentSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> AgentTokenPayload:
    """
    Agent JWT 认证依赖

    用法::

        @router.get("/xxx", dependencies=[DependsAgentJwtAuth])
        async def xxx(request: Request):
            agent = request.state.agent
            agent_hasn_id = agent.agent_hasn_id
            scopes = agent.scopes

    或作为参数注入::

        @router.get("/xxx")
        async def xxx(agent: AgentTokenPayload = DependsAgentJwtAuth):
            agent_hasn_id = agent.agent_hasn_id

    :return: AgentTokenPayload
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="缺少 Authorization header。请提供 Bearer token。",
        )

    token = credentials.credentials

    try:
        # 验证 Agent JWT
        agent_payload = await verify_agent_token(token)

        # 注入到 request.state 方便后续使用
        request.state.agent = agent_payload

        log.info(
            f"Agent JWT 认证成功: {agent_payload.agent_hasn_id} "
            f"(owner: {agent_payload.owner_hasn_id}, scopes: {agent_payload.scopes})"
        )

        return agent_payload

    except errors.TokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Agent JWT 验证失败: {str(e)}",
        )
    except Exception as e:
        log.error(f"Agent JWT 认证异常: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Agent JWT 认证失败",
        )


def require_scopes(*required_scopes: str):
    """
    Scope 权限校验装饰器

    用法::

        @router.post("/posts", dependencies=[DependsAgentJwtAuth])
        @require_scopes("community.post")
        async def create_post(agent: AgentTokenPayload = DependsAgentJwtAuth):
            ...

    :param required_scopes: 需要的权限列表
    :return: 装饰器函数
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 从 kwargs 中获取 agent 参数
            agent = kwargs.get('agent')
            if not agent:
                # 尝试从 request.state 获取
                request = kwargs.get('request')
                if request and hasattr(request.state, 'agent'):
                    agent = request.state.agent

            if not agent:
                raise HTTPException(
                    status_code=401,
                    detail="未找到 Agent 认证信息",
                )

            # 检查权限
            missing_scopes = [s for s in required_scopes if s not in agent.scopes]
            if missing_scopes:
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足，缺少 scopes: {', '.join(missing_scopes)}",
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def check_scopes(agent: AgentTokenPayload, required_scopes: list[str]) -> None:
    """
    检查 Agent 是否拥有所需的权限

    :param agent: Agent token payload
    :param required_scopes: 需要的权限列表
    :raises HTTPException: 如果权限不足
    """
    missing_scopes = [s for s in required_scopes if s not in agent.scopes]
    if missing_scopes:
        raise HTTPException(
            status_code=403,
            detail=f"权限不足，缺少 scopes: {', '.join(missing_scopes)}",
        )


# FastAPI 依赖注入快捷方式
DependsAgentJwtAuth = Depends(agent_jwt_auth)
