from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_events import app_events_dao
from backend.app.app_platform.model import AppEvents
from backend.app.app_platform.schema.app_events import CreateAppEventsParam, DeleteAppEventsParam, UpdateAppEventsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppEventsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppEvents:
        """
        获取App Event 定义

        :param db: 数据库会话
        :param pk: App Event 定义 ID
        :return:
        """
        app_events = await app_events_dao.get(db, pk)
        if not app_events:
            raise errors.NotFoundError(msg='App Event 定义不存在')
        return app_events

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App Event 定义列表

        :param db: 数据库会话
        :return:
        """
        app_events_select = await app_events_dao.get_select()
        return await paging_data(db, app_events_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppEvents]:
        """
        获取所有App Event 定义

        :param db: 数据库会话
        :return:
        """
        app_eventss = await app_events_dao.get_all(db)
        return app_eventss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppEventsParam) -> None:
        """
        创建App Event 定义

        :param db: 数据库会话
        :param obj: 创建App Event 定义参数
        :return:
        """
        await app_events_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppEventsParam) -> int:
        """
        更新App Event 定义

        :param db: 数据库会话
        :param pk: App Event 定义 ID
        :param obj: 更新App Event 定义参数
        :return:
        """
        count = await app_events_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppEventsParam) -> int:
        """
        删除App Event 定义

        :param db: 数据库会话
        :param obj: App Event 定义 ID 列表
        :return:
        """
        count = await app_events_dao.delete(db, obj.pks)
        return count


app_events_service: AppEventsService = AppEventsService()
