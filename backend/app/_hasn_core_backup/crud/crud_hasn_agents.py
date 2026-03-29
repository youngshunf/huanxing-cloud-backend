from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn_core.model import HasnAgents
from backend.app.hasn_core.schema.hasn_agents import CreateHasnAgentsParam, UpdateHasnAgentsParam


class CRUDHasnAgents(CRUDPlus[HasnAgents]):
    async def get(self, db: AsyncSession, pk: int) -> HasnAgents | None:
        """
        获取HASN Agent 

        :param db: 数据库会话
        :param pk: HASN Agent  ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取HASN Agent 列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnAgents]:
        """
        获取所有HASN Agent 

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnAgentsParam) -> None:
        """
        创建HASN Agent 

        :param db: 数据库会话
        :param obj: 创建HASN Agent 参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnAgentsParam) -> int:
        """
        更新HASN Agent 

        :param db: 数据库会话
        :param pk: HASN Agent  ID
        :param obj: 更新 HASN Agent 参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除HASN Agent 

        :param db: 数据库会话
        :param pks: HASN Agent  ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_agents_dao: CRUDHasnAgents = CRUDHasnAgents(HasnAgents)
