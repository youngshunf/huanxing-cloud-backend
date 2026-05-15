from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_scopes import app_scopes_dao
from backend.app.app_platform.model import AppScopes
from backend.app.app_platform.schema.app_scopes import CreateAppScopesParam, DeleteAppScopesParam, UpdateAppScopesParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppScopesService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppScopes:
        """
        获取应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param pk: 应用权限定义表（{domain}.* namespace） ID
        :return:
        """
        app_scopes = await app_scopes_dao.get(db, pk)
        if not app_scopes:
            raise errors.NotFoundError(msg='应用权限定义表（{domain}.* namespace）不存在')
        return app_scopes

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取应用权限定义表（{domain}.* namespace）列表

        :param db: 数据库会话
        :return:
        """
        app_scopes_select = await app_scopes_dao.get_select()
        return await paging_data(db, app_scopes_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppScopes]:
        """
        获取所有应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :return:
        """
        app_scopess = await app_scopes_dao.get_all(db)
        return app_scopess

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppScopesParam) -> None:
        """
        创建应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param obj: 创建应用权限定义表（{domain}.* namespace）参数
        :return:
        """
        await app_scopes_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppScopesParam) -> int:
        """
        更新应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param pk: 应用权限定义表（{domain}.* namespace） ID
        :param obj: 更新应用权限定义表（{domain}.* namespace）参数
        :return:
        """
        count = await app_scopes_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppScopesParam) -> int:
        """
        删除应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param obj: 应用权限定义表（{domain}.* namespace） ID 列表
        :return:
        """
        count = await app_scopes_dao.delete(db, obj.pks)
        return count


app_scopes_service: AppScopesService = AppScopesService()
