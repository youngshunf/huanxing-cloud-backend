"""Agent 权限管理服务"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud import crud_hasn_agents
from backend.app.hasn.schema.agent_scopes import (
    AgentScopesConfig,
    AgentTokenInfo,
    UpdateAgentScopesRequest,
    UpdateAgentScopesResponse,
)
from backend.common.exception import errors
from backend.common.security.agent_jwt import (
    create_agent_access_token,
    get_agent_scopes_cached,
    update_agent_scopes,
)


class AgentScopesService:
    """Agent 权限管理服务"""

    async def get_agent_scopes(self, db: AsyncSession, agent_hasn_id: str, owner_hasn_id: str) -> AgentScopesConfig:
        """查询 Agent 权限配置"""
        # 验证 Agent 归属关系
        agent = await crud_hasn_agents.get_by_hasn_id(db, hasn_id=agent_hasn_id)
        if not agent:
            raise errors.NotFoundError(msg=f'Agent {agent_hasn_id} 不存在')
        if agent.owner_id != owner_hasn_id:
            raise errors.ForbiddenError(msg='无权访问该 Agent 的权限配置')

        # 查询权限配置
        scopes_config = await get_agent_scopes_cached(agent_hasn_id, db)
        return AgentScopesConfig(
            scopes=scopes_config.get('scopes', []),
            post_needs_review=scopes_config.get('post_needs_review', False),
        )

    async def update_agent_scopes(
        self,
        db: AsyncSession,
        agent_hasn_id: str,
        owner_hasn_id: str,
        owner_user_id: int,
        request: UpdateAgentScopesRequest,
    ) -> UpdateAgentScopesResponse:
        """更新 Agent 权限配置"""
        # 验证 Agent 归属关系
        agent = await crud_hasn_agents.get_by_hasn_id(db, hasn_id=agent_hasn_id)
        if not agent:
            raise errors.NotFoundError(msg=f'Agent {agent_hasn_id} 不存在')
        if agent.owner_id != owner_hasn_id:
            raise errors.ForbiddenError(msg='无权修改该 Agent 的权限配置')

        # 更新权限配置（包括数据库更新和缓存删除）
        await update_agent_scopes(
            db=db,
            agent_hasn_id=agent_hasn_id,
            scopes=request.scopes,
            post_needs_review=request.post_needs_review,
            granted_by=owner_hasn_id,
        )

        # 签发新 Agent JWT
        agent_token = await create_agent_access_token(
            agent_hasn_id=agent_hasn_id,
            agent_name=agent.display_name or agent.agent_name,
            owner_hasn_id=owner_hasn_id,
            owner_user_id=owner_user_id,
            scopes=request.scopes,
        )

        return UpdateAgentScopesResponse(
            agent_token=AgentTokenInfo(
                access_token=agent_token.access_token,
                scopes=agent_token.scopes,
            )
        )


agent_scopes_service = AgentScopesService()
