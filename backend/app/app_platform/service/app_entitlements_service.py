from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_entitlements import app_entitlements_dao
from backend.app.app_platform.model import AppEntitlements
from backend.app.app_platform.schema.app_entitlements import CreateAppEntitlementsParam, DeleteAppEntitlementsParam, UpdateAppEntitlementsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppEntitlementsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppEntitlements:
        """
        获取App 购买凭证

        :param db: 数据库会话
        :param pk: App 购买凭证 ID
        :return:
        """
        app_entitlements = await app_entitlements_dao.get(db, pk)
        if not app_entitlements:
            raise errors.NotFoundError(msg='App 购买凭证不存在')
        return app_entitlements

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App 购买凭证列表

        :param db: 数据库会话
        :return:
        """
        app_entitlements_select = await app_entitlements_dao.get_select()
        return await paging_data(db, app_entitlements_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppEntitlements]:
        """
        获取所有App 购买凭证

        :param db: 数据库会话
        :return:
        """
        app_entitlementss = await app_entitlements_dao.get_all(db)
        return app_entitlementss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppEntitlementsParam) -> None:
        """
        创建App 购买凭证

        :param db: 数据库会话
        :param obj: 创建App 购买凭证参数
        :return:
        """
        await app_entitlements_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppEntitlementsParam) -> int:
        """
        更新App 购买凭证

        :param db: 数据库会话
        :param pk: App 购买凭证 ID
        :param obj: 更新App 购买凭证参数
        :return:
        """
        count = await app_entitlements_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppEntitlementsParam) -> int:
        """
        删除App 购买凭证

        :param db: 数据库会话
        :param obj: App 购买凭证 ID 列表
        :return:
        """
        count = await app_entitlements_dao.delete(db, obj.pks)
        return count


app_entitlements_service: AppEntitlementsService = AppEntitlementsService()
