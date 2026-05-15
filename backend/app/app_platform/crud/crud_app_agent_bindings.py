from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppAgentBindings
from backend.app.app_platform.schema.app_agent_bindings import CreateAppAgentBindingsParam, UpdateAppAgentBindingsParam


class CRUDAppAgentBindings(CRUDPlus[AppAgentBindings]):
    async def get(self, db: AsyncSession, pk: int) -> AppAgentBindings | None:
        """
        获取Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param pk: Installation 绑定的 Agent 列 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取Installation 绑定的 Agent 列列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppAgentBindings]:
        """
        获取所有Installation 绑定的 Agent 列

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppAgentBindingsParam) -> None:
        """
        创建Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param obj: 创建Installation 绑定的 Agent 列参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppAgentBindingsParam) -> int:
        """
        更新Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param pk: Installation 绑定的 Agent 列 ID
        :param obj: 更新 Installation 绑定的 Agent 列参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param pks: Installation 绑定的 Agent 列 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


app_agent_bindings_dao: CRUDAppAgentBindings = CRUDAppAgentBindings(AppAgentBindings)
