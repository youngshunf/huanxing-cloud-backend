from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_permission_grants import app_permission_grants_dao
from backend.app.app_platform.model import AppPermissionGrants
from backend.app.app_platform.schema.app_permission_grants import CreateAppPermissionGrantsParam, DeleteAppPermissionGrantsParam, UpdateAppPermissionGrantsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppPermissionGrantsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppPermissionGrants:
        """
        获取权限授予记录

        :param db: 数据库会话
        :param pk: 权限授予记录 ID
        :return:
        """
        app_permission_grants = await app_permission_grants_dao.get(db, pk)
        if not app_permission_grants:
            raise errors.NotFoundError(msg='权限授予记录不存在')
        return app_permission_grants

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取权限授予记录列表

        :param db: 数据库会话
        :return:
        """
        app_permission_grants_select = await app_permission_grants_dao.get_select()
        return await paging_data(db, app_permission_grants_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppPermissionGrants]:
        """
        获取所有权限授予记录

        :param db: 数据库会话
        :return:
        """
        app_permission_grantss = await app_permission_grants_dao.get_all(db)
        return app_permission_grantss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppPermissionGrantsParam) -> None:
        """
        创建权限授予记录

        :param db: 数据库会话
        :param obj: 创建权限授予记录参数
        :return:
        """
        await app_permission_grants_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppPermissionGrantsParam) -> int:
        """
        更新权限授予记录

        :param db: 数据库会话
        :param pk: 权限授予记录 ID
        :param obj: 更新权限授予记录参数
        :return:
        """
        count = await app_permission_grants_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppPermissionGrantsParam) -> int:
        """
        删除权限授予记录

        :param db: 数据库会话
        :param obj: 权限授予记录 ID 列表
        :return:
        """
        count = await app_permission_grants_dao.delete(db, obj.pks)
        return count


app_permission_grants_service: AppPermissionGrantsService = AppPermissionGrantsService()
