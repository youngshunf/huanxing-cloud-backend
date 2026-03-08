from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorHotTopic
from backend.app.creator.schema.hx_creator_hot_topic import CreateHxCreatorHotTopicParam, UpdateHxCreatorHotTopicParam


class CRUDHxCreatorHotTopic(CRUDPlus[HxCreatorHotTopic]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorHotTopic | None:
        """
        获取热榜快照

        :param db: 数据库会话
        :param pk: 热榜快照 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取热榜快照列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorHotTopic]:
        """
        获取所有热榜快照

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHxCreatorHotTopicParam) -> None:
        """
        创建热榜快照

        :param db: 数据库会话
        :param obj: 创建热榜快照参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorHotTopicParam) -> int:
        """
        更新热榜快照

        :param db: 数据库会话
        :param pk: 热榜快照 ID
        :param obj: 更新 热榜快照参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除热榜快照

        :param db: 数据库会话
        :param pks: 热榜快照 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_hot_topic_dao: CRUDHxCreatorHotTopic = CRUDHxCreatorHotTopic(HxCreatorHotTopic)
