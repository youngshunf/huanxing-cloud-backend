from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_collection_items import hasn_collection_items_dao
from backend.app.hasn.model import HasnCollectionItems
from backend.app.hasn.schema.hasn_collection_items import CreateHasnCollectionItemsParam, DeleteHasnCollectionItemsParam, UpdateHasnCollectionItemsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnCollectionItemsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnCollectionItems:
        """
        获取社区收藏项

        :param db: 数据库会话
        :param pk: 社区收藏项 ID
        :return:
        """
        hasn_collection_items = await hasn_collection_items_dao.get(db, pk)
        if not hasn_collection_items:
            raise errors.NotFoundError(msg='社区收藏项不存在')
        return hasn_collection_items

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取社区收藏项列表

        :param db: 数据库会话
        :return:
        """
        hasn_collection_items_select = await hasn_collection_items_dao.get_select()
        return await paging_data(db, hasn_collection_items_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnCollectionItems]:
        """
        获取所有社区收藏项

        :param db: 数据库会话
        :return:
        """
        hasn_collection_items_list = await hasn_collection_items_dao.get_all(db)
        return hasn_collection_items_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnCollectionItemsParam) -> None:
        """
        创建社区收藏项

        :param db: 数据库会话
        :param obj: 创建社区收藏项参数
        :return:
        """
        await hasn_collection_items_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnCollectionItemsParam) -> int:
        """
        更新社区收藏项

        :param db: 数据库会话
        :param pk: 社区收藏项 ID
        :param obj: 更新社区收藏项参数
        :return:
        """
        count = await hasn_collection_items_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnCollectionItemsParam) -> int:
        """
        删除社区收藏项

        :param db: 数据库会话
        :param obj: 社区收藏项 ID 列表
        :return:
        """
        count = await hasn_collection_items_dao.delete(db, obj.pks)
        return count


hasn_collection_items_service: HasnCollectionItemsService = HasnCollectionItemsService()
