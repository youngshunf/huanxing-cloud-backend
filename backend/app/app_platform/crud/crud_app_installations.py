from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppInstallations
from backend.app.app_platform.schema.app_installations import UpdateAppInstallationsParam


class CRUDAppInstallations(CRUDPlus[AppInstallations]):
    async def get(self, db: AsyncSession, pk: int) -> AppInstallations | None:
        """
        获取App 安装记录

        :param db: 数据库会话
        :param pk: App 安装记录 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取App 安装记录列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppInstallations]:
        """
        获取所有App 安装记录

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: Any) -> AppInstallations:
        """
        创建App 安装记录

        :param db: 数据库会话
        :param obj: 创建App 安装记录参数
        :return:
        """
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppInstallationsParam) -> int:
        """
        更新App 安装记录

        :param db: 数据库会话
        :param pk: App 安装记录 ID
        :param obj: 更新 App 安装记录参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除App 安装记录

        :param db: 数据库会话
        :param pks: App 安装记录 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_installation_id(self, db: AsyncSession, installation_id: str) -> AppInstallations | None:
        """
        根据 installation_id 获取安装记录

        :param db: 数据库会话
        :param installation_id: Installation ID
        :return:
        """
        return await self.select_model_by_column(db, installation_id=installation_id)

    async def get_by_owner(self, db: AsyncSession, owner_id: str) -> list[AppInstallations]:
        """
        根据 owner_id 获取所有安装记录

        :param db: 数据库会话
        :param owner_id: Owner ID
        :return:
        """
        return list(await self.select_models(db, owner_id=str(owner_id)))


app_installations_dao: CRUDAppInstallations = CRUDAppInstallations(AppInstallations)
