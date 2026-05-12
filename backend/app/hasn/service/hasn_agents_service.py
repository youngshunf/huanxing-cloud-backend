from typing import Any, Protocol, Sequence
import re

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
    async def append_agent_sync_event(self, db: AsyncSession, *, owner_id: str, agent: Any, event_type: str) -> None: ...


class SqlAlchemyAgentProfileGateway:
    async def owns_owner(self, db: AsyncSession, *, owner_id: str, user_id: int) -> bool:
        from backend.app.hasn.model import HasnHumans
        import sqlalchemy as sa

        result = await db.execute(
            sa.select(HasnHumans.id).where(
                HasnHumans.hasn_id == owner_id,
                HasnHumans.user_id == user_id,
                HasnHumans.status == 'active',
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_template(self, db: AsyncSession, *, template_id: str) -> Any | None:
        from backend.app.hasn.model import HasnAgentTemplates
        import sqlalchemy as sa

        result = await db.execute(
            sa.select(HasnAgentTemplates).where(
                HasnAgentTemplates.template_id == template_id,
                HasnAgentTemplates.status == 'active',
            ).limit(1)
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
            avatar_url=payload.get('avatar'),
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
        return CloudCreateAgentResponse(
            agent=_agent_snapshot(agent),
            agent_key=agent_key,
            already_exists=already_exists,
        )

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
        server_revision = max((snapshot.profile_revision for snapshot in snapshots), default=request.after_revision or 0)
        return AgentSyncResponse(owner_id=request.owner_id, server_revision=server_revision, agents=snapshots)

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
        'description': request.description or getattr(template, 'default_description', None) or getattr(template, 'description', None),
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
    return AgentSnapshot(
        hasn_id=getattr(agent, 'hasn_id'),
        star_id=getattr(agent, 'star_id', ''),
        owner_id=getattr(agent, 'owner_id'),
        agent_name=getattr(agent, 'agent_name'),
        display_name=getattr(agent, 'display_name'),
        description=getattr(agent, 'description', None),
        avatar=getattr(agent, 'avatar', None),
        type=getattr(agent, 'type', 'desktop') or 'desktop',
        role=getattr(agent, 'role', 'specialist') or 'specialist',
        node_id=getattr(agent, 'node_id', None),
        capabilities=getattr(agent, 'capabilities', None),
        template_id=getattr(agent, 'template_id', None),
        skills=getattr(agent, 'skills', None),
        soul_md=getattr(agent, 'soul_md', None),
        user_md=getattr(agent, 'user_md', None),
        profile_revision=int(getattr(agent, 'profile_revision', 1) or 1),
        status=getattr(agent, 'status', 'active') or 'active',
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
    async def create(*, db: AsyncSession, obj: CreateHasnAgentsParam) -> None:
        """
        创建HASN Agent

        附带写入 hasn_contacts（owner→agent 的 service 关系，trust_level=5/connected），
        与 hasn_auth.register_hasn_agent 行为对齐：所有 agent 创建路径
        （app create_my_hasn_agents / admin create_hasn_agents）一律自动落 contacts。
        ON CONFLICT (owner_id, peer_id, relation_type) DO NOTHING 幂等。

        :param db: 数据库会话
        :param obj: 创建HASN Agent 参数
        :return:
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
