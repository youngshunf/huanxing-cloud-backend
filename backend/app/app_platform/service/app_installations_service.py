from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_installations import app_installations_dao
from backend.app.app_platform.model import AppInstallations
from backend.app.app_platform.schema.app_installations import CreateAppInstallationsParam, DeleteAppInstallationsParam, UpdateAppInstallationsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppInstallationsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppInstallations:
        """
        获取App 安装记录

        :param db: 数据库会话
        :param pk: App 安装记录 ID
        :return:
        """
        app_installations = await app_installations_dao.get(db, pk)
        if not app_installations:
            raise errors.NotFoundError(msg='App 安装记录不存在')
        return app_installations

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App 安装记录列表

        :param db: 数据库会话
        :return:
        """
        app_installations_select = await app_installations_dao.get_select()
        return await paging_data(db, app_installations_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppInstallations]:
        """
        获取所有App 安装记录

        :param db: 数据库会话
        :return:
        """
        app_installationss = await app_installations_dao.get_all(db)
        return app_installationss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppInstallationsParam) -> None:
        """
        创建App 安装记录

        :param db: 数据库会话
        :param obj: 创建App 安装记录参数
        :return:
        """
        await app_installations_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppInstallationsParam) -> int:
        """
        更新App 安装记录

        :param db: 数据库会话
        :param pk: App 安装记录 ID
        :param obj: 更新App 安装记录参数
        :return:
        """
        count = await app_installations_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppInstallationsParam) -> int:
        """
        删除App 安装记录

        :param db: 数据库会话
        :param obj: App 安装记录 ID 列表
        :return:
        """
        count = await app_installations_dao.delete(db, obj.pks)
        return count


app_installations_service: AppInstallationsService = AppInstallationsService()
