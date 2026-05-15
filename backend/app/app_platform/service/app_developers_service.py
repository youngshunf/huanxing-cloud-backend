from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_developers import app_developers_dao
from backend.app.app_platform.model import AppDevelopers
from backend.app.app_platform.schema.app_developers import CreateAppDevelopersParam, DeleteAppDevelopersParam, UpdateAppDevelopersParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppDevelopersService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppDevelopers:
        """
        获取应用开发者

        :param db: 数据库会话
        :param pk: 应用开发者 ID
        :return:
        """
        app_developers = await app_developers_dao.get(db, pk)
        if not app_developers:
            raise errors.NotFoundError(msg='应用开发者不存在')
        return app_developers

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取应用开发者列表

        :param db: 数据库会话
        :return:
        """
        app_developers_select = await app_developers_dao.get_select()
        return await paging_data(db, app_developers_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppDevelopers]:
        """
        获取所有应用开发者

        :param db: 数据库会话
        :return:
        """
        app_developerss = await app_developers_dao.get_all(db)
        return app_developerss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppDevelopersParam) -> None:
        """
        创建应用开发者

        :param db: 数据库会话
        :param obj: 创建应用开发者参数
        :return:
        """
        await app_developers_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppDevelopersParam) -> int:
        """
        更新应用开发者

        :param db: 数据库会话
        :param pk: 应用开发者 ID
        :param obj: 更新应用开发者参数
        :return:
        """
        count = await app_developers_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppDevelopersParam) -> int:
        """
        删除应用开发者

        :param db: 数据库会话
        :param obj: 应用开发者 ID 列表
        :return:
        """
        count = await app_developers_dao.delete(db, obj.pks)
        return count


app_developers_service: AppDevelopersService = AppDevelopersService()
