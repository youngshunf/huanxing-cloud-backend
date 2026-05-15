from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppVersions
from backend.app.app_platform.schema.app_versions import CreateAppVersionsParam, UpdateAppVersionsParam


class CRUDAppVersions(CRUDPlus[AppVersions]):
    async def get(self, db: AsyncSession, pk: int) -> AppVersions | None:
        """
        获取App 版本

        :param db: 数据库会话
        :param pk: App 版本 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取App 版本列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppVersions]:
        """
        获取所有App 版本

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj):
        """
        创建App 版本

        :param db: 数据库会话
        :param obj: 创建App 版本参数
        :return:
        """
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppVersionsParam) -> int:
        """
        更新App 版本

        :param db: 数据库会话
        :param pk: App 版本 ID
        :param obj: 更新 App 版本参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除App 版本

        :param db: 数据库会话
        :param pks: App 版本 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)
    async def get_by_app_and_version(self, db: AsyncSession, app_id: str, version: str) -> AppVersions | None:
        """
        根据 app_id 和 version 获取版本

        :param db: 数据库会话
        :param app_id: App ID
        :param version: 版本号
        :return:
        """
        return await self.select_model_by_column(db, app_id=app_id, version=version)


app_versions_dao: CRUDAppVersions = CRUDAppVersions(AppVersions)
