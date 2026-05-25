"""
MCP 认证中间件

使用 FastAPI Depends 机制验证 Agent JWT 并注入 AgentContext
"""
from typing import Annotated

from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.dataclasses import AgentTokenPayload
from backend.common.security.agent_jwt import verify_agent_token
from backend.common.exception import errors
from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.database.db import async_db_session
from backend.utils.timezone import timezone


class AgentContext:
    """Agent 执行上下文"""

    def __init__(
        self,
        hasn_id: str,
        owner_id: int,
        scopes: list[str],
        agent_status: str,
        metadata: dict,
        agent_name: str = "",
        owner_hasn_id: str | None = None,
        session_uuid: str | None = None,
        token_payload: AgentTokenPayload | None = None,
    ):
        self.hasn_id = hasn_id
        self.owner_id = owner_id
        self.scopes = scopes
        self.agent_status = agent_status
        self.metadata = metadata
        self.agent_name = agent_name
        self.owner_hasn_id = owner_hasn_id
        self.session_uuid = session_uuid
        self._token_payload = token_payload

    @classmethod
    def from_token_payload(
        cls,
        payload: AgentTokenPayload,
        *,
        agent_status: str,
        metadata: dict | None = None,
    ) -> "AgentContext":
        return cls(
            hasn_id=payload.agent_hasn_id,
            owner_id=payload.owner_user_id,
            scopes=payload.scopes,
            agent_status=agent_status,
            metadata=metadata or {},
            agent_name=payload.agent_name,
            owner_hasn_id=payload.owner_hasn_id,
            session_uuid=payload.session_uuid,
            token_payload=payload,
        )

    def to_token_payload(self) -> AgentTokenPayload:
        if self._token_payload is not None:
            return self._token_payload
        if self.owner_hasn_id is None or self.session_uuid is None:
            raise errors.TokenError(msg='AgentContext 缺少 Agent JWT 字段')
        return AgentTokenPayload(
            agent_hasn_id=self.hasn_id,
            agent_name=self.agent_name,
            owner_hasn_id=self.owner_hasn_id,
            owner_user_id=self.owner_id,
            scopes=self.scopes,
            session_uuid=self.session_uuid,
            expire_time=timezone.now(),
        )

    @property
    def agent_hasn_id(self) -> str:
        return self.hasn_id

    @property
    def owner_user_id(self) -> int:
        return self.owner_id

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

    # 验证 Agent JWT and its revocable Redis-backed session record.
    try:
        payload = await verify_agent_token(token)
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
        agent = await hasn_agents_dao.get_by_hasn_id(db, hasn_id=x_hasn_agent_id)

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

    return AgentContext.from_token_payload(payload, agent_status=agent.status)


# 类型别名，方便在路由中使用
AgentContextDep = Annotated[AgentContext, Depends(get_agent_context)]
