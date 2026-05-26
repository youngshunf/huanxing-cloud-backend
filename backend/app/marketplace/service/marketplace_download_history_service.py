from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.crud.crud_marketplace_download_history import marketplace_download_history_dao
from backend.app.marketplace.model import MarketplaceDownloadHistory
from backend.app.marketplace.schema.marketplace_download_history import CreateMarketplaceDownloadHistoryParam, DeleteMarketplaceDownloadHistoryParam, UpdateMarketplaceDownloadHistoryParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class MarketplaceDownloadHistoryService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> MarketplaceDownloadHistory:
        """
        获取技能市场下载历史

        :param db: 数据库会话
        :param pk: 技能市场下载历史 ID
        :return:
        """
        marketplace_download_history = await marketplace_download_history_dao.get(db, pk)
        if not marketplace_download_history:
            raise errors.NotFoundError(msg='技能市场下载历史不存在')
        return marketplace_download_history

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取技能市场下载历史列表

        :param db: 数据库会话
        :return:
        """
        marketplace_download_history_select = await marketplace_download_history_dao.get_select()
        return await paging_data(db, marketplace_download_history_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[MarketplaceDownloadHistory]:
        """
        获取所有技能市场下载历史

        :param db: 数据库会话
        :return:
        """
        marketplace_download_history_list = await marketplace_download_history_dao.get_all(db)
        return marketplace_download_history_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateMarketplaceDownloadHistoryParam) -> None:
        """
        创建技能市场下载历史

        :param db: 数据库会话
        :param obj: 创建技能市场下载历史参数
        :return:
        """
        await marketplace_download_history_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateMarketplaceDownloadHistoryParam) -> int:
        """
        更新技能市场下载历史

        :param db: 数据库会话
        :param pk: 技能市场下载历史 ID
        :param obj: 更新技能市场下载历史参数
        :return:
        """
        count = await marketplace_download_history_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteMarketplaceDownloadHistoryParam) -> int:
        """
        删除技能市场下载历史

        :param db: 数据库会话
        :param obj: 技能市场下载历史 ID 列表
        :return:
        """
        count = await marketplace_download_history_dao.delete(db, obj.pks)
        return count


marketplace_download_history_service: MarketplaceDownloadHistoryService = MarketplaceDownloadHistoryService()
