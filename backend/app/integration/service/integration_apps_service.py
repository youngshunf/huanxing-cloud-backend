from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.integration.crud.crud_integration_apps import integration_apps_dao
from backend.app.integration.model import IntegrationApps
from backend.app.integration.schema.integration_apps import CreateIntegrationAppsParam, DeleteIntegrationAppsParam, UpdateIntegrationAppsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class IntegrationAppsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> IntegrationApps:
        """
        获取第三方应用集成配置

        :param db: 数据库会话
        :param pk: 第三方应用集成配置 ID
        :return:
        """
        integration_apps = await integration_apps_dao.get(db, pk)
        if not integration_apps:
            raise errors.NotFoundError(msg='第三方应用集成配置不存在')
        return integration_apps

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取第三方应用集成配置列表

        :param db: 数据库会话
        :return:
        """
        integration_apps_select = await integration_apps_dao.get_select()
        return await paging_data(db, integration_apps_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[IntegrationApps]:
        """
        获取所有第三方应用集成配置

        :param db: 数据库会话
        :return:
        """
        integration_apps_list = await integration_apps_dao.get_all(db)
        return integration_apps_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateIntegrationAppsParam) -> None:
        """
        创建第三方应用集成配置

        :param db: 数据库会话
        :param obj: 创建第三方应用集成配置参数
        :return:
        """
        await integration_apps_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateIntegrationAppsParam) -> int:
        """
        更新第三方应用集成配置

        :param db: 数据库会话
        :param pk: 第三方应用集成配置 ID
        :param obj: 更新第三方应用集成配置参数
        :return:
        """
        count = await integration_apps_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteIntegrationAppsParam) -> int:
        """
        删除第三方应用集成配置

        :param db: 数据库会话
        :param obj: 第三方应用集成配置 ID 列表
        :return:
        """
        count = await integration_apps_dao.delete(db, obj.pks)
        return count


integration_apps_service: IntegrationAppsService = IntegrationAppsService()
