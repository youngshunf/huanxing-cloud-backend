from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_publish import hx_creator_publish_dao
from backend.app.creator.model import HxCreatorPublish
from backend.app.creator.schema.hx_creator_publish import CreateHxCreatorPublishParam, DeleteHxCreatorPublishParam, UpdateHxCreatorPublishParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorPublishService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorPublish:
        """
        获取发布记录

        :param db: 数据库会话
        :param pk: 发布记录 ID
        :return:
        """
        hx_creator_publish = await hx_creator_publish_dao.get(db, pk)
        if not hx_creator_publish:
            raise errors.NotFoundError(msg='发布记录不存在')
        return hx_creator_publish

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取发布记录列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_publish_select = await hx_creator_publish_dao.get_select()
        return await paging_data(db, hx_creator_publish_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorPublish]:
        """
        获取所有发布记录

        :param db: 数据库会话
        :return:
        """
        hx_creator_publishs = await hx_creator_publish_dao.get_all(db)
        return hx_creator_publishs

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorPublishParam) -> None:
        """
        创建发布记录

        :param db: 数据库会话
        :param obj: 创建发布记录参数
        :return:
        """
        await hx_creator_publish_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorPublishParam) -> int:
        """
        更新发布记录

        :param db: 数据库会话
        :param pk: 发布记录 ID
        :param obj: 更新发布记录参数
        :return:
        """
        count = await hx_creator_publish_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorPublishParam) -> int:
        """
        删除发布记录

        :param db: 数据库会话
        :param obj: 发布记录 ID 列表
        :return:
        """
        count = await hx_creator_publish_dao.delete(db, obj.pks)
        return count


hx_creator_publish_service: HxCreatorPublishService = HxCreatorPublishService()
