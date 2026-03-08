from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_media import hx_creator_media_dao
from backend.app.creator.model import HxCreatorMedia
from backend.app.creator.schema.hx_creator_media import CreateHxCreatorMediaParam, DeleteHxCreatorMediaParam, UpdateHxCreatorMediaParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorMediaService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorMedia:
        """
        获取素材库

        :param db: 数据库会话
        :param pk: 素材库 ID
        :return:
        """
        hx_creator_media = await hx_creator_media_dao.get(db, pk)
        if not hx_creator_media:
            raise errors.NotFoundError(msg='素材库不存在')
        return hx_creator_media

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取素材库列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_media_select = await hx_creator_media_dao.get_select()
        return await paging_data(db, hx_creator_media_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorMedia]:
        """
        获取所有素材库

        :param db: 数据库会话
        :return:
        """
        hx_creator_medias = await hx_creator_media_dao.get_all(db)
        return hx_creator_medias

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorMediaParam) -> None:
        """
        创建素材库

        :param db: 数据库会话
        :param obj: 创建素材库参数
        :return:
        """
        await hx_creator_media_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorMediaParam) -> int:
        """
        更新素材库

        :param db: 数据库会话
        :param pk: 素材库 ID
        :param obj: 更新素材库参数
        :return:
        """
        count = await hx_creator_media_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorMediaParam) -> int:
        """
        删除素材库

        :param db: 数据库会话
        :param obj: 素材库 ID 列表
        :return:
        """
        count = await hx_creator_media_dao.delete(db, obj.pks)
        return count


hx_creator_media_service: HxCreatorMediaService = HxCreatorMediaService()
