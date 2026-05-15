from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppEvents
from backend.app.app_platform.schema.app_events import CreateAppEventsParam, UpdateAppEventsParam


class CRUDAppEvents(CRUDPlus[AppEvents]):
    async def get(self, db: AsyncSession, pk: int) -> AppEvents | None:
        """
        获取App Event 定义

        :param db: 数据库会话
        :param pk: App Event 定义 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取App Event 定义列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppEvents]:
        """
        获取所有App Event 定义

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppEventsParam) -> None:
        """
        创建App Event 定义

        :param db: 数据库会话
        :param obj: 创建App Event 定义参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppEventsParam) -> int:
        """
        更新App Event 定义

        :param db: 数据库会话
        :param pk: App Event 定义 ID
        :param obj: 更新 App Event 定义参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除App Event 定义

        :param db: 数据库会话
        :param pks: App Event 定义 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


app_events_dao: CRUDAppEvents = CRUDAppEvents(AppEvents)
