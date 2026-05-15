from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppDevelopers
from backend.app.app_platform.schema.app_developers import CreateAppDevelopersParam, UpdateAppDevelopersParam


class CRUDAppDevelopers(CRUDPlus[AppDevelopers]):
    async def get(self, db: AsyncSession, pk: int) -> AppDevelopers | None:
        """
        获取应用开发者

        :param db: 数据库会话
        :param pk: 应用开发者 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取应用开发者列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppDevelopers]:
        """
        获取所有应用开发者

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj):
        """
        创建应用开发者

        :param db: 数据库会话
        :param obj: 创建应用开发者参数
        :return:
        """
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppDevelopersParam) -> int:
        """
        更新应用开发者

        :param db: 数据库会话
        :param pk: 应用开发者 ID
        :param obj: 更新 应用开发者参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除应用开发者

        :param db: 数据库会话
        :param pks: 应用开发者 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


app_developers_dao: CRUDAppDevelopers = CRUDAppDevelopers(AppDevelopers)
