"""
MCP 认证中间件

使用 FastAPI Depends 机制验证 Agent JWT 并注入 AgentContext
"""
from typing import Annotated

from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.security.agent_jwt import jwt_decode_agent
from backend.common.exception import errors
from backend.app.hasn.service.hasn_agents_service import HasnAgentsService
from backend.database.db import async_db_session


class AgentContext:
    """Agent 执行上下文"""

    def __init__(
        self,
        hasn_id: str,
        owner_id: int,
        scopes: list[str],
        agent_status: str,
        metadata: dict
    ):
        self.hasn_id = hasn_id
        self.owner_id = owner_id
        self.scopes = scopes
        self.agent_status = agent_status
        self.metadata = metadata

    def has_scope(self, scope: str) -> bool:
        """检查是否有指定权限"""
        return scope in self.scopes

    def require_scopes(self, *required_scopes: str) -> None:
        """要求必须有指定权限"""
        missing = [s for s in required_scopes if s not in self.scopes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scopes: {', '.join(missing)}"
            )


async def get_agent_context(
    authorization: Annotated[str, Header()],
    x_hasn_agent_id: Annotated[str, Header(alias="X-HASN-Agent-ID")]
) -> AgentContext:
    """
    验证 Agent JWT 并返回执行上下文

    使用 FastAPI Depends 机制，在路由层注入 AgentContext

    Args:
        authorization: Bearer token
        x_hasn_agent_id: Agent HASN ID

    Returns:
        AgentContext: Agent 执行上下文

    Raises:
        HTTPException: 认证失败
    """
    # 提取 token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )

    token = authorization[7:]  # 移除 "Bearer " 前缀

    # 验证 Agent JWT
    try:
        payload = jwt_decode_agent(token)
    except errors.TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

    # 验证 hasn_id 匹配
    if payload.agent_hasn_id != x_hasn_agent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent ID mismatch"
        )

    # 加载 Agent 信息验证状态
    async with async_db_session() as db:
        agent_service = HasnAgentsService()
        agent = await agent_service.get_by_hasn_id(db, hasn_id=x_hasn_agent_id)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )

        # 检查 Agent 状态
        if agent.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Agent is {agent.status}"
            )

    return AgentContext(
        hasn_id=payload.agent_hasn_id,
        owner_id=payload.owner_user_id,
        scopes=payload.scopes,
        agent_status=agent.status,
        metadata={}
    )


# 类型别名，方便在路由中使用
AgentContextDep = Annotated[AgentContext, Depends(get_agent_context)]
