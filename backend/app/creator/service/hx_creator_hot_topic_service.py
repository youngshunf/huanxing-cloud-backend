from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_hot_topic import hx_creator_hot_topic_dao
from backend.app.creator.model import HxCreatorHotTopic
from backend.app.creator.schema.hx_creator_hot_topic import CreateHxCreatorHotTopicParam, DeleteHxCreatorHotTopicParam, UpdateHxCreatorHotTopicParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorHotTopicService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorHotTopic:
        """
        获取热榜快照

        :param db: 数据库会话
        :param pk: 热榜快照 ID
        :return:
        """
        hx_creator_hot_topic = await hx_creator_hot_topic_dao.get(db, pk)
        if not hx_creator_hot_topic:
            raise errors.NotFoundError(msg='热榜快照不存在')
        return hx_creator_hot_topic

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取热榜快照列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_hot_topic_select = await hx_creator_hot_topic_dao.get_select()
        return await paging_data(db, hx_creator_hot_topic_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorHotTopic]:
        """
        获取所有热榜快照

        :param db: 数据库会话
        :return:
        """
        hx_creator_hot_topics = await hx_creator_hot_topic_dao.get_all(db)
        return hx_creator_hot_topics

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorHotTopicParam) -> None:
        """
        创建热榜快照

        :param db: 数据库会话
        :param obj: 创建热榜快照参数
        :return:
        """
        await hx_creator_hot_topic_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorHotTopicParam) -> int:
        """
        更新热榜快照

        :param db: 数据库会话
        :param pk: 热榜快照 ID
        :param obj: 更新热榜快照参数
        :return:
        """
        count = await hx_creator_hot_topic_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorHotTopicParam) -> int:
        """
        删除热榜快照

        :param db: 数据库会话
        :param obj: 热榜快照 ID 列表
        :return:
        """
        count = await hx_creator_hot_topic_dao.delete(db, obj.pks)
        return count


hx_creator_hot_topic_service: HxCreatorHotTopicService = HxCreatorHotTopicService()
