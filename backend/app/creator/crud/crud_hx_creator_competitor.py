from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorCompetitor
from backend.app.creator.schema.hx_creator_competitor import CreateHxCreatorCompetitorParam, UpdateHxCreatorCompetitorParam


class CRUDHxCreatorCompetitor(CRUDPlus[HxCreatorCompetitor]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorCompetitor | None:
        """
        获取竞品账号

        :param db: 数据库会话
        :param pk: 竞品账号 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取竞品账号列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorCompetitor]:
        """
        获取所有竞品账号

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHxCreatorCompetitorParam) -> None:
        """
        创建竞品账号

        :param db: 数据库会话
        :param obj: 创建竞品账号参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorCompetitorParam) -> int:
        """
        更新竞品账号

        :param db: 数据库会话
        :param pk: 竞品账号 ID
        :param obj: 更新 竞品账号参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除竞品账号

        :param db: 数据库会话
        :param pks: 竞品账号 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_competitor_dao: CRUDHxCreatorCompetitor = CRUDHxCreatorCompetitor(HxCreatorCompetitor)
