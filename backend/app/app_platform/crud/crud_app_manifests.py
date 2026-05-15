from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppManifests
from backend.app.app_platform.schema.app_manifests import CreateAppManifestsParam, UpdateAppManifestsParam


class CRUDAppManifests(CRUDPlus[AppManifests]):
    async def get(self, db: AsyncSession, pk: int) -> AppManifests | None:
        """
        获取App 清单

        :param db: 数据库会话
        :param pk: App 清单 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取App 清单列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppManifests]:
        """
        获取所有App 清单

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj):
        """
        创建App 清单

        :param db: 数据库会话
        :param obj: 创建App 清单参数
        :return:
        """
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppManifestsParam) -> int:
        """
        更新App 清单

        :param db: 数据库会话
        :param pk: App 清单 ID
        :param obj: 更新 App 清单参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除App 清单

        :param db: 数据库会话
        :param pks: App 清单 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_app_id(self, db: AsyncSession, app_id: str) -> AppManifests | None:
        """
        根据 app_id 获取应用

        :param db: 数据库会话
        :param app_id: App ID
        :return:
        """
        return await self.select_model_by_column(db, app_id=app_id)


app_manifests_dao: CRUDAppManifests = CRUDAppManifests(AppManifests)
