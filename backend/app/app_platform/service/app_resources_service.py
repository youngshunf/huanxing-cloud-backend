from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_resources import app_resources_dao
from backend.app.app_platform.model import AppResources
from backend.app.app_platform.schema.app_resources import CreateAppResourcesParam, DeleteAppResourcesParam, UpdateAppResourcesParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppResourcesService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppResources:
        """
        获取App Resource 定义

        :param db: 数据库会话
        :param pk: App Resource 定义 ID
        :return:
        """
        app_resources = await app_resources_dao.get(db, pk)
        if not app_resources:
            raise errors.NotFoundError(msg='App Resource 定义不存在')
        return app_resources

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App Resource 定义列表

        :param db: 数据库会话
        :return:
        """
        app_resources_select = await app_resources_dao.get_select()
        return await paging_data(db, app_resources_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppResources]:
        """
        获取所有App Resource 定义

        :param db: 数据库会话
        :return:
        """
        app_resourcess = await app_resources_dao.get_all(db)
        return app_resourcess

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppResourcesParam) -> None:
        """
        创建App Resource 定义

        :param db: 数据库会话
        :param obj: 创建App Resource 定义参数
        :return:
        """
        await app_resources_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppResourcesParam) -> int:
        """
        更新App Resource 定义

        :param db: 数据库会话
        :param pk: App Resource 定义 ID
        :param obj: 更新App Resource 定义参数
        :return:
        """
        count = await app_resources_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppResourcesParam) -> int:
        """
        删除App Resource 定义

        :param db: 数据库会话
        :param obj: App Resource 定义 ID 列表
        :return:
        """
        count = await app_resources_dao.delete(db, obj.pks)
        return count


app_resources_service: AppResourcesService = AppResourcesService()
