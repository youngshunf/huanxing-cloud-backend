"""
Agent Key 认证模块

Agent（OpenClaw 插件）调用后端 API 时使用静态 Agent Key 认证。
与 JWT 认证分离，Agent 不需要登录获取 token。

认证方式: Header `X-Agent-Key: <key>`
路由前缀: /api/v1/{module}/agent/

@author Ysf (auto-generated)
"""
import hashlib
import hmac
from typing import Any

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from backend.core.conf import settings
from backend.common.log import log


# Header 定义
_agent_key_header = APIKeyHeader(name="X-Agent-Key", auto_error=False)


def verify_agent_key(api_key: str | None) -> bool:
    """
    验证 Agent Key

    使用 hmac.compare_digest 防止时序攻击。
    支持配置多个 key（逗号分隔），便于 key 轮换。

    :param api_key: 请求中携带的 Agent Key
    :return: True if valid
    """
    if not api_key:
        return False

    # 支持多 key（逗号分隔），用于 key 轮换
    valid_keys = [k.strip() for k in settings.AGENT_SECRET_KEY.split(",") if k.strip()]

    for valid_key in valid_keys:
        if hmac.compare_digest(api_key, valid_key):
            return True

    return False


async def agent_auth(
    request: Request,
    api_key: str | None = Security(_agent_key_header),
) -> dict[str, Any]:
    """
    Agent 认证依赖

    用法::

        @router.get("/xxx", dependencies=[Depends(agent_auth)])
        async def xxx(request: Request):
            agent_info = request.state.agent_info
            server_id = agent_info["server_id"]

    或作为参数注入::

        @router.get("/xxx")
        async def xxx(agent: dict = Depends(agent_auth)):
            server_id = agent["server_id"]

    :return: {authenticated: True, server_id, key_prefix}
    """
    if not verify_agent_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Agent Key 无效。请在请求头中提供 X-Agent-Key。",
        )

    # 提取 server_id（从 header 获取，可选）
    server_id = request.headers.get("X-Server-Id", "unknown")

    agent_info = {
        "authenticated": True,
        "server_id": server_id,
        "key_prefix": api_key[:8] + "..." if api_key and len(api_key) > 8 else "***",
    }

    # 注入到 request.state 方便后续使用
    request.state.agent_info = agent_info

    return agent_info


# FastAPI 依赖注入快捷方式
DependsAgentAuth = Depends(agent_auth)
