from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.integration.model import IntegrationApps
from backend.app.integration.schema.integration_apps import CreateIntegrationAppsParam, UpdateIntegrationAppsParam


class CRUDIntegrationApps(CRUDPlus[IntegrationApps]):
    async def get_by_app_id(self, db: AsyncSession, app_id: str) -> IntegrationApps | None:
        """
        根据应用 ID 获取配置

        :param db: 数据库会话
        :param app_id: 应用 ID
        :return:
        """
        stmt = select(self.model).where(self.model.app_id == app_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get(self, db: AsyncSession, pk: int) -> IntegrationApps | None:
        """
        获取第三方应用集成配置

        :param db: 数据库会话
        :param pk: 第三方应用集成配置 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取第三方应用集成配置列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[IntegrationApps]:
        """
        获取所有第三方应用集成配置

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateIntegrationAppsParam) -> None:
        """
        创建第三方应用集成配置

        :param db: 数据库会话
        :param obj: 创建第三方应用集成配置参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateIntegrationAppsParam) -> int:
        """
        更新第三方应用集成配置

        :param db: 数据库会话
        :param pk: 第三方应用集成配置 ID
        :param obj: 更新 第三方应用集成配置参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除第三方应用集成配置

        :param db: 数据库会话
        :param pks: 第三方应用集成配置 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


integration_apps_dao: CRUDIntegrationApps = CRUDIntegrationApps(IntegrationApps)
