from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_tools import app_tools_dao
from backend.app.app_platform.model import AppTools
from backend.app.app_platform.schema.app_tools import CreateAppToolsParam, DeleteAppToolsParam, UpdateAppToolsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppToolsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppTools:
        """
        获取App Tool 定义

        :param db: 数据库会话
        :param pk: App Tool 定义 ID
        :return:
        """
        app_tools = await app_tools_dao.get(db, pk)
        if not app_tools:
            raise errors.NotFoundError(msg='App Tool 定义不存在')
        return app_tools

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App Tool 定义列表

        :param db: 数据库会话
        :return:
        """
        app_tools_select = await app_tools_dao.get_select()
        return await paging_data(db, app_tools_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppTools]:
        """
        获取所有App Tool 定义

        :param db: 数据库会话
        :return:
        """
        app_toolss = await app_tools_dao.get_all(db)
        return app_toolss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppToolsParam) -> None:
        """
        创建App Tool 定义

        :param db: 数据库会话
        :param obj: 创建App Tool 定义参数
        :return:
        """
        await app_tools_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppToolsParam) -> int:
        """
        更新App Tool 定义

        :param db: 数据库会话
        :param pk: App Tool 定义 ID
        :param obj: 更新App Tool 定义参数
        :return:
        """
        count = await app_tools_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppToolsParam) -> int:
        """
        删除App Tool 定义

        :param db: 数据库会话
        :param obj: App Tool 定义 ID 列表
        :return:
        """
        count = await app_tools_dao.delete(db, obj.pks)
        return count


app_tools_service: AppToolsService = AppToolsService()
