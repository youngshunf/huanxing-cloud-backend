"""Agent 权限管理服务（三态 + catalog，D2/D3/Q2）

设计事实源：93-doc §P5、13-doc §5.1/§5.2。
- get_agent_scopes：返回三态配置（default_mode + capability_modes）。
- update_agent_scopes：D3 写表 + 失效缓存，**不重签 JWT**（凭证与授权解耦，开关即时生效）。
- get_scope_catalog：D2 聚合可见工具 → 按来源分组 → 每条标三态 + scopes.py 元数据。
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn.schema.agent_scopes import (
    AgentScopesConfig,
    ScopeCatalogResponse,
    UpdateAgentScopesRequest,
    UpdateAgentScopesResponse,
)
from backend.common.exception import errors
from backend.common.security.agent_jwt import (
    get_agent_scopes_cached,
    update_agent_modes,
)


class AgentScopesService:
    """Agent 权限管理服务"""

    async def _assert_owns(self, db: AsyncSession, agent_hasn_id: str, owner_hasn_id: str, *, write: bool) -> None:
        """校验该 Agent 归属当前主人，否则 404/403。"""
        agent = await hasn_agents_dao.get_by_hasn_id(db, hasn_id=agent_hasn_id)
        if not agent:
            raise errors.NotFoundError(msg=f'Agent {agent_hasn_id} 不存在')
        if agent.owner_id != owner_hasn_id:
            verb = '修改' if write else '访问'
            raise errors.ForbiddenError(msg=f'无权{verb}该 Agent 的权限配置')

    def _config_from_policy(self, cfg: dict) -> AgentScopesConfig:
        return AgentScopesConfig(
            scopes=cfg.get('scopes', []),
            post_needs_review=cfg.get('post_needs_review', False),
            default_mode=cfg.get('default_mode', 'allow'),
            capability_modes=cfg.get('capability_modes', {}),
        )

    async def get_agent_scopes(self, db: AsyncSession, agent_hasn_id: str, owner_hasn_id: str) -> AgentScopesConfig:
        """查询 Agent 权限配置（含三态）。"""
        await self._assert_owns(db, agent_hasn_id, owner_hasn_id, write=False)
        cfg = await get_agent_scopes_cached(agent_hasn_id, db)
        return self._config_from_policy(cfg)

    async def update_agent_scopes(
        self,
        db: AsyncSession,
        agent_hasn_id: str,
        owner_hasn_id: str,
        request: UpdateAgentScopesRequest,
    ) -> UpdateAgentScopesResponse:
        """更新 Agent 三态授权（D3：写表 + 失效缓存，不重签 JWT，即时生效）。"""
        await self._assert_owns(db, agent_hasn_id, owner_hasn_id, write=True)

        await update_agent_modes(
            db=db,
            agent_hasn_id=agent_hasn_id,
            default_mode=request.default_mode,
            capability_modes=request.capability_modes,
            post_needs_review=request.post_needs_review,
        )

        cfg = await get_agent_scopes_cached(agent_hasn_id, db)
        return UpdateAgentScopesResponse(config=self._config_from_policy(cfg))

    async def get_scope_catalog(self, db: AsyncSession, agent_hasn_id: str, owner_hasn_id: str) -> ScopeCatalogResponse:
        """工具/scope 目录（D2，按来源分组，每条带三态当前值）。

        聚合「全部已注册可见工具」的 required_scopes，叠加 scopes.py 展示元数据；
        external 分组结构保留但为空（Q5）。对象级关系门控（维度②）不进 catalog。
        """
        await self._assert_owns(db, agent_hasn_id, owner_hasn_id, write=False)

        from backend.app.mcp.auth import AgentContext
        from backend.app.mcp.server import mcp_server

        cfg = await get_agent_scopes_cached(agent_hasn_id, db)
        # catalog 仅按 owner_hasn_id 鉴权、按 agent_hasn_id 取策略聚合；owner_user_id 不参与隔离，置 0。
        ctx = AgentContext(
            hasn_id=agent_hasn_id,
            owner_id=0,
            scopes=cfg.get('scopes', []),
            agent_status='active',
            metadata={},
            owner_hasn_id=owner_hasn_id,
            session_uuid=f'catalog:{agent_hasn_id}',
            default_mode=cfg.get('default_mode', 'allow'),
            capability_modes=cfg.get('capability_modes', {}),
        )
        # 确保 App 工具已投影进注册表（builtin + 已发布 manifest），catalog 才能含 app 分组。
        await mcp_server._load_app_tools(ctx)
        catalog = mcp_server.tool_directory.build_scope_catalog(ctx)
        return ScopeCatalogResponse.model_validate(catalog)


agent_scopes_service = AgentScopesService()
