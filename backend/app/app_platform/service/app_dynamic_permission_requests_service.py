from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_dynamic_permission_requests import app_dynamic_permission_requests_dao
from backend.app.app_platform.model import AppDynamicPermissionRequests
from backend.app.app_platform.schema.app_dynamic_permission_requests import CreateAppDynamicPermissionRequestsParam, DeleteAppDynamicPermissionRequestsParam, UpdateAppDynamicPermissionRequestsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppDynamicPermissionRequestsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppDynamicPermissionRequests:
        """
        获取动态权限请求

        :param db: 数据库会话
        :param pk: 动态权限请求 ID
        :return:
        """
        app_dynamic_permission_requests = await app_dynamic_permission_requests_dao.get(db, pk)
        if not app_dynamic_permission_requests:
            raise errors.NotFoundError(msg='动态权限请求不存在')
        return app_dynamic_permission_requests

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取动态权限请求列表

        :param db: 数据库会话
        :return:
        """
        app_dynamic_permission_requests_select = await app_dynamic_permission_requests_dao.get_select()
        return await paging_data(db, app_dynamic_permission_requests_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppDynamicPermissionRequests]:
        """
        获取所有动态权限请求

        :param db: 数据库会话
        :return:
        """
        app_dynamic_permission_requestss = await app_dynamic_permission_requests_dao.get_all(db)
        return app_dynamic_permission_requestss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppDynamicPermissionRequestsParam) -> None:
        """
        创建动态权限请求

        :param db: 数据库会话
        :param obj: 创建动态权限请求参数
        :return:
        """
        await app_dynamic_permission_requests_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppDynamicPermissionRequestsParam) -> int:
        """
        更新动态权限请求

        :param db: 数据库会话
        :param pk: 动态权限请求 ID
        :param obj: 更新动态权限请求参数
        :return:
        """
        count = await app_dynamic_permission_requests_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppDynamicPermissionRequestsParam) -> int:
        """
        删除动态权限请求

        :param db: 数据库会话
        :param obj: 动态权限请求 ID 列表
        :return:
        """
        count = await app_dynamic_permission_requests_dao.delete(db, obj.pks)
        return count


app_dynamic_permission_requests_service: AppDynamicPermissionRequestsService = AppDynamicPermissionRequestsService()
