from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_platform_scopes import platform_scopes_dao
from backend.app.app_platform.model import PlatformScopes
from backend.app.app_platform.schema.platform_scopes import CreatePlatformScopesParam, DeletePlatformScopesParam, UpdatePlatformScopesParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class PlatformScopesService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> PlatformScopes:
        """
        获取平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param pk: 平台权限定义表（hasn.* namespace） ID
        :return:
        """
        platform_scopes = await platform_scopes_dao.get(db, pk)
        if not platform_scopes:
            raise errors.NotFoundError(msg='平台权限定义表（hasn.* namespace）不存在')
        return platform_scopes

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取平台权限定义表（hasn.* namespace）列表

        :param db: 数据库会话
        :return:
        """
        platform_scopes_select = await platform_scopes_dao.get_select()
        return await paging_data(db, platform_scopes_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[PlatformScopes]:
        """
        获取所有平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :return:
        """
        platform_scopess = await platform_scopes_dao.get_all(db)
        return platform_scopess

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreatePlatformScopesParam) -> None:
        """
        创建平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param obj: 创建平台权限定义表（hasn.* namespace）参数
        :return:
        """
        await platform_scopes_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdatePlatformScopesParam) -> int:
        """
        更新平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param pk: 平台权限定义表（hasn.* namespace） ID
        :param obj: 更新平台权限定义表（hasn.* namespace）参数
        :return:
        """
        count = await platform_scopes_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeletePlatformScopesParam) -> int:
        """
        删除平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param obj: 平台权限定义表（hasn.* namespace） ID 列表
        :return:
        """
        count = await platform_scopes_dao.delete(db, obj.pks)
        return count


platform_scopes_service: PlatformScopesService = PlatformScopesService()
