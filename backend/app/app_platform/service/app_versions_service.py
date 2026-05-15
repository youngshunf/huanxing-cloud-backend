from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_versions import app_versions_dao
from backend.app.app_platform.model import AppVersions
from backend.app.app_platform.schema.app_versions import CreateAppVersionsParam, DeleteAppVersionsParam, UpdateAppVersionsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppVersionsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppVersions:
        """
        获取App 版本

        :param db: 数据库会话
        :param pk: App 版本 ID
        :return:
        """
        app_versions = await app_versions_dao.get(db, pk)
        if not app_versions:
            raise errors.NotFoundError(msg='App 版本不存在')
        return app_versions

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App 版本列表

        :param db: 数据库会话
        :return:
        """
        app_versions_select = await app_versions_dao.get_select()
        return await paging_data(db, app_versions_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppVersions]:
        """
        获取所有App 版本

        :param db: 数据库会话
        :return:
        """
        app_versionss = await app_versions_dao.get_all(db)
        return app_versionss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppVersionsParam) -> None:
        """
        创建App 版本

        :param db: 数据库会话
        :param obj: 创建App 版本参数
        :return:
        """
        await app_versions_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppVersionsParam) -> int:
        """
        更新App 版本

        :param db: 数据库会话
        :param pk: App 版本 ID
        :param obj: 更新App 版本参数
        :return:
        """
        count = await app_versions_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppVersionsParam) -> int:
        """
        删除App 版本

        :param db: 数据库会话
        :param obj: App 版本 ID 列表
        :return:
        """
        count = await app_versions_dao.delete(db, obj.pks)
        return count


app_versions_service: AppVersionsService = AppVersionsService()
