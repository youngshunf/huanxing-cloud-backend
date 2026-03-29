from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.crud_hasn_agents import hasn_agents_dao
from backend.app.hasn_core.model import HasnAgents
from backend.app.hasn_core.schema.hasn_agents import CreateHasnAgentsParam, DeleteHasnAgentsParam, UpdateHasnAgentsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


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

        :param db: 数据库会话
        :param obj: 创建HASN Agent 参数
        :return:
        """
        await hasn_agents_dao.create(db, obj)

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
