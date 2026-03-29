from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.hasn_core.model import HasnHumans
from backend.app.hasn_core.schema.hasn_humans import CreateHasnHumansParam, UpdateHasnHumansParam


class CRUDHasnHumans(CRUDPlus[HasnHumans]):
    async def get(self, db: AsyncSession, pk: int) -> HasnHumans | None:
        """
        获取HASN Human 用户

        :param db: 数据库会话
        :param pk: HASN Human 用户 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取HASN Human 用户列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HasnHumans]:
        """
        获取所有HASN Human 用户

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHasnHumansParam) -> None:
        """
        创建HASN Human 用户

        :param db: 数据库会话
        :param obj: 创建HASN Human 用户参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHasnHumansParam) -> int:
        """
        更新HASN Human 用户

        :param db: 数据库会话
        :param pk: HASN Human 用户 ID
        :param obj: 更新 HASN Human 用户参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除HASN Human 用户

        :param db: 数据库会话
        :param pks: HASN Human 用户 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hasn_humans_dao: CRUDHasnHumans = CRUDHasnHumans(HasnHumans)
