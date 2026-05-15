from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_manifests import app_manifests_dao
from backend.app.app_platform.model import AppManifests
from backend.app.app_platform.schema.app_manifests import CreateAppManifestsParam, DeleteAppManifestsParam, UpdateAppManifestsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppManifestsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppManifests:
        """
        获取App 清单

        :param db: 数据库会话
        :param pk: App 清单 ID
        :return:
        """
        app_manifests = await app_manifests_dao.get(db, pk)
        if not app_manifests:
            raise errors.NotFoundError(msg='App 清单不存在')
        return app_manifests

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App 清单列表

        :param db: 数据库会话
        :return:
        """
        app_manifests_select = await app_manifests_dao.get_select()
        return await paging_data(db, app_manifests_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppManifests]:
        """
        获取所有App 清单

        :param db: 数据库会话
        :return:
        """
        app_manifestss = await app_manifests_dao.get_all(db)
        return app_manifestss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppManifestsParam) -> None:
        """
        创建App 清单

        :param db: 数据库会话
        :param obj: 创建App 清单参数
        :return:
        """
        await app_manifests_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppManifestsParam) -> int:
        """
        更新App 清单

        :param db: 数据库会话
        :param pk: App 清单 ID
        :param obj: 更新App 清单参数
        :return:
        """
        count = await app_manifests_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppManifestsParam) -> int:
        """
        删除App 清单

        :param db: 数据库会话
        :param obj: App 清单 ID 列表
        :return:
        """
        count = await app_manifests_dao.delete(db, obj.pks)
        return count


app_manifests_service: AppManifestsService = AppManifestsService()
