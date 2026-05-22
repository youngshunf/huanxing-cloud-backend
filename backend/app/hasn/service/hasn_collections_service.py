from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_collections import hasn_collections_dao
from backend.app.hasn.model import HasnCollections
from backend.app.hasn.schema.hasn_collections import CreateHasnCollectionsParam, DeleteHasnCollectionsParam, UpdateHasnCollectionsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnCollectionsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnCollections:
        """
        获取社区收藏夹

        :param db: 数据库会话
        :param pk: 社区收藏夹 ID
        :return:
        """
        hasn_collections = await hasn_collections_dao.get(db, pk)
        if not hasn_collections:
            raise errors.NotFoundError(msg='社区收藏夹不存在')
        return hasn_collections

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取社区收藏夹列表

        :param db: 数据库会话
        :return:
        """
        hasn_collections_select = await hasn_collections_dao.get_select()
        return await paging_data(db, hasn_collections_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnCollections]:
        """
        获取所有社区收藏夹

        :param db: 数据库会话
        :return:
        """
        hasn_collections_list = await hasn_collections_dao.get_all(db)
        return hasn_collections_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnCollectionsParam) -> None:
        """
        创建社区收藏夹

        :param db: 数据库会话
        :param obj: 创建社区收藏夹参数
        :return:
        """
        await hasn_collections_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnCollectionsParam) -> int:
        """
        更新社区收藏夹

        :param db: 数据库会话
        :param pk: 社区收藏夹 ID
        :param obj: 更新社区收藏夹参数
        :return:
        """
        count = await hasn_collections_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnCollectionsParam) -> int:
        """
        删除社区收藏夹

        :param db: 数据库会话
        :param obj: 社区收藏夹 ID 列表
        :return:
        """
        count = await hasn_collections_dao.delete(db, obj.pks)
        return count


hasn_collections_service: HasnCollectionsService = HasnCollectionsService()
