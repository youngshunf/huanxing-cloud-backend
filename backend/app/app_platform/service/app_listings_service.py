from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_listings import app_listings_dao
from backend.app.app_platform.model import AppListings
from backend.app.app_platform.schema.app_listings import CreateAppListingsParam, DeleteAppListingsParam, UpdateAppListingsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppListingsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppListings:
        """
        获取应用市场列表

        :param db: 数据库会话
        :param pk: 应用市场列表 ID
        :return:
        """
        app_listings = await app_listings_dao.get(db, pk)
        if not app_listings:
            raise errors.NotFoundError(msg='应用市场列表不存在')
        return app_listings

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取应用市场列表列表

        :param db: 数据库会话
        :return:
        """
        app_listings_select = await app_listings_dao.get_select()
        return await paging_data(db, app_listings_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppListings]:
        """
        获取所有应用市场列表

        :param db: 数据库会话
        :return:
        """
        app_listingss = await app_listings_dao.get_all(db)
        return app_listingss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppListingsParam) -> None:
        """
        创建应用市场列表

        :param db: 数据库会话
        :param obj: 创建应用市场列表参数
        :return:
        """
        await app_listings_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppListingsParam) -> int:
        """
        更新应用市场列表

        :param db: 数据库会话
        :param pk: 应用市场列表 ID
        :param obj: 更新应用市场列表参数
        :return:
        """
        count = await app_listings_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppListingsParam) -> int:
        """
        删除应用市场列表

        :param db: 数据库会话
        :param obj: 应用市场列表 ID 列表
        :return:
        """
        count = await app_listings_dao.delete(db, obj.pks)
        return count


app_listings_service: AppListingsService = AppListingsService()
