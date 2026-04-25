from typing import Any, Sequence

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn.model import HasnAgents
from backend.app.hasn.model.hasn_contacts import HasnContacts
from backend.app.hasn.schema.hasn_agents import CreateHasnAgentsParam, DeleteHasnAgentsParam, UpdateHasnAgentsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.utils.timezone import timezone


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
