import re

from collections.abc import Sequence
from typing import Any, Protocol

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn.model import HasnAgents
from backend.app.hasn.model.hasn_contacts import HasnContacts
from backend.app.hasn.schema.hasn_agents import (
    AgentSnapshot,
    AgentSyncRequest,
    AgentSyncResponse,
    CloudCreateAgentRequest,
    CloudCreateAgentResponse,
    CreateHasnAgentsParam,
    DeleteHasnAgentsParam,
    UpdateAgentBindingRequest,
    UpdateAgentProfileRequest,
    UpdateAgentProfileResponse,
    UpdateHasnAgentsParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone


class AgentProfileGateway(Protocol):
    async def owns_owner(self, db: AsyncSession, *, owner_id: str, user_id: int) -> bool: ...
    async def get_template(self, db: AsyncSession, *, template_id: str) -> Any | None: ...
    async def create_agent(self, db: AsyncSession, payload: dict[str, Any]) -> tuple[Any, str | None, bool]: ...
    async def list_owner_agents(
        self, db: AsyncSession, *, owner_id: str, after_revision: int | None = None
    ) -> list[Any]: ...
    async def append_agent_sync_event(
        self, db: AsyncSession, *, owner_id: str, agent: Any, event_type: str
    ) -> None: ...


class SqlAlchemyAgentProfileGateway:
    async def owns_owner(self, db: AsyncSession, *, owner_id: str, user_id: int) -> bool:
        import sqlalchemy as sa

        from backend.app.hasn.model import HasnHumans

        result = await db.execute(
            sa
            .select(HasnHumans.id)
            .where(
                HasnHumans.hasn_id == owner_id,
                HasnHumans.user_id == user_id,
                HasnHumans.status == 'active',
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_template(self, db: AsyncSession, *, template_id: str) -> Any | None:
        import sqlalchemy as sa

        from backend.app.hasn.model import HasnAgentTemplates

        result = await db.execute(
            sa
            .select(HasnAgentTemplates)
            .where(
                HasnAgentTemplates.template_id == template_id,
                HasnAgentTemplates.status == 'active',
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_agent(self, db: AsyncSession, payload: dict[str, Any]) -> tuple[Any, str | None, bool]:
        from backend.app.hasn.service.hasn_auth import register_hasn_agent

        result = await register_hasn_agent(
            db=db,
            owner_hasn_id=payload['owner_id'],
            agent_name=payload['agent_name'],
            display_name=payload['display_name'],
            agent_type=payload.get('agent_type') or 'desktop',
            node_id=payload.get('node_id'),
            role=payload.get('role') or 'specialist',
            description=payload.get('description'),
            capabilities=payload.get('capabilities'),
            created_via='client',
            avatar=payload.get('avatar'),
            template_id=payload.get('template_id'),
            skills=payload.get('skills'),
            soul_md=payload.get('soul_md'),
            user_md=payload.get('user_md'),
        )
        agent = result['agent']
        for attr in ('template_id', 'skills', 'soul_md', 'user_md'):
            if hasattr(agent, attr):
                setattr(agent, attr, payload.get(attr))
        if hasattr(agent, 'profile_source'):
            agent.profile_source = 'cloud'
        if not getattr(agent, 'profile_revision', None):
            agent.profile_revision = 1
        await db.flush()
        return agent, result.get('agent_key'), bool(result.get('already_exists'))

    async def list_owner_agents(
        self, db: AsyncSession, *, owner_id: str, after_revision: int | None = None
    ) -> list[Any]:
        import sqlalchemy as sa

        stmt = sa.select(HasnAgents).where(HasnAgents.owner_id == owner_id)
        if after_revision is not None and hasattr(HasnAgents, 'profile_revision'):
            stmt = stmt.where(HasnAgents.profile_revision > after_revision)
        stmt = stmt.order_by(HasnAgents.id.asc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def append_agent_sync_event(self, db: AsyncSession, *, owner_id: str, agent: Any, event_type: str) -> None:
        from backend.app.hasn.service.hasn_sync_service import SqlAlchemySyncGateway

        await SqlAlchemySyncGateway()._append_sync_event(
            db,
            owner_id=owner_id,
            hasn_id=agent.hasn_id,
            event_type=event_type,
            aggregate_type='agent',
            aggregate_id=agent.hasn_id,
            payload={'agent': _agent_snapshot(agent).model_dump(mode='json')},
        )


class HasnAgentProfileService:
    def __init__(self, gateway: AgentProfileGateway | None = None) -> None:
        self.gateway = gateway or SqlAlchemyAgentProfileGateway()

    async def create_cloud_first(
        self, db: AsyncSession, request: CloudCreateAgentRequest, *, user_id: int | None = None
    ) -> CloudCreateAgentResponse:
        await self._assert_owner_access(db, owner_id=request.owner_id, user_id=user_id)
        template = await self.gateway.get_template(db, template_id=request.template_id) if request.template_id else None
        payload = _merge_agent_create_payload(request, template)
        agent, agent_key, already_exists = await self.gateway.create_agent(db, payload)
        await self.gateway.append_agent_sync_event(
            db,
            owner_id=request.owner_id,
            agent=agent,
            event_type='agent.updated' if already_exists else 'agent.created',
        )

        # 为新创建的 Agent 插入默认权限配置并签发 JWT
        agent_token_info = None
        if not already_exists:
            try:
                from backend.app.hasn.schema.hasn_agents import AgentTokenInfo
                from backend.common.security.agent_jwt import (
                    create_agent_access_token,
                    create_default_agent_scopes,
                    get_agent_scopes_cached,
                )

                # 插入默认权限配置
                await create_default_agent_scopes(db, agent.hasn_id, request.owner_id)

                # 获取权限配置
                scopes_config = await get_agent_scopes_cached(agent.hasn_id, db)
                scopes = scopes_config.get('scopes', [])

                # 签发 Agent JWT
                agent_token = await create_agent_access_token(
                    agent_hasn_id=agent.hasn_id,
                    agent_name=agent.display_name or agent.agent_name,
                    owner_hasn_id=request.owner_id,
                    owner_user_id=user_id or 0,
                    scopes=scopes,
                )

                agent_token_info = AgentTokenInfo(
                    access_token=agent_token.access_token,
                    scopes=agent_token.scopes,
                )
            except Exception as e:
                from backend.common.log import log

                log.error(f'为 Agent {agent.hasn_id} 签发 JWT 失败: {e}')
                # JWT 签发失败不影响 Agent 创建

        return CloudCreateAgentResponse(
            agent=_agent_snapshot(agent),
            agent_key=agent_key,
            agent_token=agent_token_info,
            already_exists=already_exists,
        )

    async def update_profile_cloud_first(
        self,
        db: AsyncSession,
        *,
        owner_id: str,
        hasn_id: str,
        request: UpdateAgentProfileRequest,
        user_id: int | None = None,
    ) -> UpdateAgentProfileResponse:
        """云端权威更新 Agent profile。

        daemon 调用：云端先落库 → 返回最新快照 → daemon 据此回写本地镜像。
        所有字段都是 partial：只有显式传入的字段才会被写。
        """
        import sqlalchemy as sa

        await self._assert_owner_access(db, owner_id=owner_id, user_id=user_id)

        agent = (
            await db.execute(
                sa.select(HasnAgents).where(
                    HasnAgents.hasn_id == hasn_id,
                    HasnAgents.owner_id == owner_id,
                )
            )
        ).scalar_one_or_none()
        if agent is None:
            raise errors.NotFoundError(msg='ERR_HASN_AGENT_NOT_FOUND')

        provided = request.model_dump(exclude_unset=True)
        if not provided:
            return UpdateAgentProfileResponse(agent=_agent_snapshot(agent))

        if 'status' in provided and provided['status'] is not None:
            if provided['status'] not in _ALLOWED_STATUS_VALUES:
                raise errors.RequestError(
                    msg=f'ERR_HASN_AGENT_STATUS_INVALID:{provided["status"]}'
                )

        if 'star_id' in provided and provided['star_id'] is not None:
            new_star_id = provided['star_id']
            if new_star_id != agent.star_id:
                conflict = (
                    await db.execute(
                        sa.select(HasnAgents.id).where(
                            HasnAgents.star_id == new_star_id,
                            HasnAgents.id != agent.id,
                        )
                    )
                ).scalar_one_or_none()
                if conflict is not None:
                    raise errors.RequestError(msg='ERR_HASN_AGENT_STAR_ID_TAKEN')
                agent.star_id = new_star_id

        if 'display_name' in provided and provided['display_name'] is not None:
            agent.display_name = provided['display_name']
        if 'description' in provided:
            agent.description = provided['description']
        if 'avatar' in provided:
            agent.avatar = provided['avatar']
        if 'role' in provided and provided['role'] is not None:
            agent.role = provided['role']
        if 'tags' in provided and provided['tags'] is not None:
            agent.tags = list(provided['tags'])
        if 'capability_set_id' in provided:
            agent.capability_set_id = provided['capability_set_id']
        if 'persona_ref' in provided:
            agent.persona_ref = provided['persona_ref']
        if 'status' in provided and provided['status'] is not None:
            agent.status = provided['status']

        if hasattr(agent, 'profile_revision'):
            agent.profile_revision = (agent.profile_revision or 1) + 1
        await db.flush()

        await self.gateway.append_agent_sync_event(
            db,
            owner_id=owner_id,
            agent=agent,
            event_type='agent.updated',
        )

        return UpdateAgentProfileResponse(agent=_agent_snapshot(agent))

    async def sync_agents(
        self, db: AsyncSession, request: AgentSyncRequest, *, user_id: int | None = None
    ) -> AgentSyncResponse:
        await self._assert_owner_access(db, owner_id=request.owner_id, user_id=user_id)
        agents = await self.gateway.list_owner_agents(
            db,
            owner_id=request.owner_id,
            after_revision=request.after_revision,
        )
        if not request.include_disabled:
            agents = [agent for agent in agents if getattr(agent, 'status', 'active') == 'active']
        snapshots = [_agent_snapshot(agent) for agent in agents]
        server_revision = max(
            (snapshot.profile_revision for snapshot in snapshots), default=request.after_revision or 0
        )
        return AgentSyncResponse(owner_id=request.owner_id, server_revision=server_revision, agents=snapshots)

    async def update_binding(
        self,
        db: AsyncSession,
        hasn_id: str,
        request: UpdateAgentBindingRequest,
        *,
        user_id: int | None = None,
    ) -> AgentSnapshot:
        import sqlalchemy as sa
        from backend.utils.timezone import timezone as tz

        result = await db.execute(
            sa.select(HasnAgents).where(HasnAgents.hasn_id == hasn_id).limit(1)
        )
        agent = result.scalar_one_or_none()
        if agent is None:
            raise errors.NotFoundError(msg=f'agent {hasn_id} not found')
        if user_id is not None and not await self.gateway.owns_owner(db, owner_id=agent.owner_id, user_id=user_id):
            raise errors.AuthorizationError(msg='ERR_HASN_OWNER_ACCESS_DENIED')
        if request.binding_status not in _ALLOWED_BINDING_STATUS_VALUES:
            raise errors.RequestError(
                msg=f'ERR_HASN_AGENT_BINDING_STATUS_INVALID:{request.binding_status}'
            )

        now_unix = int(tz.now().timestamp())
        await db.execute(
            sa.update(HasnAgents)
            .where(HasnAgents.hasn_id == hasn_id)
            .values(
                binding_node_id=request.binding_node_id,
                binding_status=request.binding_status,
                binding_updated_at=now_unix,
            )
        )
        await db.refresh(agent)
        return _agent_snapshot(agent)

    async def update_heartbeat(
        self,
        db: AsyncSession,
        hasn_id: str,
        request: 'AgentHeartbeatRequest',
        *,
        user_id: int | None = None,
    ) -> 'AgentHeartbeatResponse':
        """更新 agent 心跳状态。"""
        import sqlalchemy as sa
        from datetime import datetime

        from backend.app.hasn.schema.hasn_agents import AgentHeartbeatResponse

        result = await db.execute(
            sa.select(HasnAgents).where(HasnAgents.hasn_id == hasn_id).limit(1)
        )
        agent = result.scalar_one_or_none()
        if agent is None:
            raise errors.NotFoundError(msg=f'agent {hasn_id} not found')
        if user_id is not None and not await self.gateway.owns_owner(db, owner_id=agent.owner_id, user_id=user_id):
            raise errors.AuthorizationError(msg='ERR_HASN_OWNER_ACCESS_DENIED')

        # 更新在线状态和心跳时间
        await db.execute(
            sa.update(HasnAgents)
            .where(HasnAgents.hasn_id == hasn_id)
            .values(
                binding_node_id=request.node_id,
                online_status=request.online_status,
                last_heartbeat_at=datetime.fromtimestamp(request.last_heartbeat_at),
            )
        )
        await db.commit()
        return AgentHeartbeatResponse(success=True)

    async def _assert_owner_access(self, db: AsyncSession, *, owner_id: str, user_id: int | None) -> None:
        if user_id is None:
            return
        if not await self.gateway.owns_owner(db, owner_id=owner_id, user_id=user_id):
            raise errors.AuthorizationError(msg='ERR_HASN_OWNER_ACCESS_DENIED')


def _merge_agent_create_payload(request: CloudCreateAgentRequest, template: Any | None) -> dict[str, Any]:
    return {
        'owner_id': request.owner_id,
        'template_id': request.template_id,
        'agent_name': _resolve_agent_slug(request, template),
        'display_name': request.display_name,
        'description': request.description
        or getattr(template, 'default_description', None)
        or getattr(template, 'description', None),
        'avatar': request.avatar or getattr(template, 'avatar', None),
        'skills': request.skills if request.skills is not None else getattr(template, 'default_skills', None),
        'soul_md': request.soul_md if request.soul_md is not None else getattr(template, 'default_soul_md', None),
        'user_md': request.user_md if request.user_md is not None else getattr(template, 'default_user_md', None),
        'runtime_type': request.runtime_type or getattr(template, 'default_runtime_type', None) or 'hermes',
        'node_id': request.node_id,
        'agent_type': request.agent_type,
        'role': request.role,
        'capabilities': request.capabilities,
    }


_SLUG_RE = re.compile(r'^[a-z][a-z0-9_-]{0,63}$')

# 云端 hasn_agents.status 的允许值集合：业务态 + 生命周期态合并落同一列。
_ALLOWED_STATUS_VALUES: frozenset[str] = frozenset(
    {'active', 'disabled', 'revoked', 'archived', 'deleted'}
)
_ALLOWED_BINDING_STATUS_VALUES: frozenset[str] = frozenset(
    {'unbound', 'binding', 'bound', 'failed'}
)


def _resolve_agent_slug(request: CloudCreateAgentRequest, template: Any | None) -> str:
    if request.agent_name and _SLUG_RE.match(request.agent_name):
        return request.agent_name
    for candidate in (
        getattr(template, 'agent_name', None),
        getattr(template, 'template_id', None),
        request.template_id,
    ):
        if isinstance(candidate, str) and _SLUG_RE.match(candidate):
            return candidate
    slug = re.sub(r'[^a-z0-9_-]+', '-', request.display_name.lower()).strip('-_')[:64]
    if slug and _SLUG_RE.match(slug):
        return slug
    return 'agent'


def _agent_snapshot(agent: Any) -> AgentSnapshot:
    raw_tags = getattr(agent, 'tags', None)
    if isinstance(raw_tags, list):
        tags = [str(item) for item in raw_tags if item is not None]
    else:
        tags = []
    return AgentSnapshot(
        hasn_id=agent.hasn_id,
        star_id=getattr(agent, 'star_id', ''),
        owner_id=agent.owner_id,
        agent_name=agent.agent_name,
        display_name=agent.display_name,
        description=getattr(agent, 'description', None),
        avatar=getattr(agent, 'avatar', None),
        type=getattr(agent, 'type', 'desktop') or 'desktop',
        role=getattr(agent, 'role', 'specialist') or 'specialist',
        node_id=getattr(agent, 'node_id', None),
        capabilities=getattr(agent, 'capabilities', None),
        capability_set_id=getattr(agent, 'capability_set_id', None),
        persona_ref=getattr(agent, 'persona_ref', None),
        tags=tags,
        template_id=getattr(agent, 'template_id', None),
        skills=getattr(agent, 'skills', None),
        soul_md=getattr(agent, 'soul_md', None),
        user_md=getattr(agent, 'user_md', None),
        profile_revision=int(getattr(agent, 'profile_revision', 1) or 1),
        status=getattr(agent, 'status', 'active') or 'active',
        social_enabled=bool(getattr(agent, 'social_enabled', False)),
        binding_node_id=getattr(agent, 'binding_node_id', None),
        binding_status=getattr(agent, 'binding_status', 'unbound') or 'unbound',
        binding_updated_at=getattr(agent, 'binding_updated_at', None),
        updated_time=getattr(agent, 'updated_time', None),
    )


agent_profile_service = HasnAgentProfileService()


class HasnAgentsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnAgents:
        """
        获取HASN Agent

        :param db: 数据库会话
        :param pk: HASN Agent  ID
        :return:
        """
        hasn_agents = await hasn_agents_dao.get(db, pk)
        if not hasn_agents:
            raise errors.NotFoundError(msg='HASN Agent 不存在')
        return hasn_agents

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN Agent 列表

        :param db: 数据库会话
        :return:
        """
        hasn_agents_select = await hasn_agents_dao.get_select()
        return await paging_data(db, hasn_agents_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnAgents]:
        """
        获取所有HASN Agent

        :param db: 数据库会话
        :return:
        """
        hasn_agentss = await hasn_agents_dao.get_all(db)
        return hasn_agentss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnAgentsParam, user_id: int) -> dict[str, Any]:
        """
        创建HASN Agent

        附带写入 hasn_contacts（owner→agent 的 service 关系，trust_level=5/connected），
        与 hasn_auth.register_hasn_agent 行为对齐：所有 agent 创建路径
        （app create_my_hasn_agents / admin create_hasn_agents）一律自动落 contacts。
        ON CONFLICT (owner_id, peer_id, relation_type) DO NOTHING 幂等。

        :param db: 数据库会话
        :param obj: 创建HASN Agent 参数
        :param user_id: 用户 ID
        :return: Agent 信息及 JWT
        """
        await hasn_agents_dao.create(db, obj)
        await db.execute(
            pg_insert(HasnContacts)
            .values(
                owner_id=obj.owner_id,
                peer_id=obj.hasn_id,
                peer_owner_id=obj.owner_id,
                peer_type='agent',
                relation_type='service',
                trust_level=5,
                status='connected',
                channel_source='system',
                subscription=False,
                interaction_count=0,
                custom_permissions={},
                nickname=obj.name,
                connected_at=timezone.now(),
            )
            .on_conflict_do_nothing(
                index_elements=['owner_id', 'peer_id', 'relation_type'],
            )
        )

        # 签发 Agent JWT
        from backend.common.security.agent_jwt import create_agent_access_token, get_agent_scopes_cached

        scopes_config = await get_agent_scopes_cached(obj.hasn_id, db)
        agent_token = await create_agent_access_token(
            agent_hasn_id=obj.hasn_id,
            agent_name=obj.name,
            owner_hasn_id=obj.owner_id,
            owner_user_id=user_id,
            scopes=scopes_config['scopes'],
        )

        return {
            'hasn_id': obj.hasn_id,
            'owner_id': obj.owner_id,
            'name': obj.name,
            'access_token': agent_token.access_token,
            'scopes': agent_token.scopes,
            'expire_time': agent_token.access_token_expire_time.isoformat(),
        }

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnAgentsParam) -> int:
        """
        更新HASN Agent

        :param db: 数据库会话
        :param pk: HASN Agent  ID
        :param obj: 更新HASN Agent 参数
        :return:
        """
        count = await hasn_agents_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnAgentsParam) -> int:
        """
        删除HASN Agent

        :param db: 数据库会话
        :param obj: HASN Agent  ID 列表
        :return:
        """
        count = await hasn_agents_dao.delete(db, obj.pks)
        return count


hasn_agents_service: HasnAgentsService = HasnAgentsService()
