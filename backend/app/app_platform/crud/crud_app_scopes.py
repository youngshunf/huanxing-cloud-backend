from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppScopes
from backend.app.app_platform.schema.app_scopes import CreateAppScopesParam, UpdateAppScopesParam


class CRUDAppScopes(CRUDPlus[AppScopes]):
    async def get(self, db: AsyncSession, pk: int) -> AppScopes | None:
        """
        获取应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param pk: 应用权限定义表（{domain}.* namespace） ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取应用权限定义表（{domain}.* namespace）列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppScopes]:
        """
        获取所有应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppScopesParam) -> None:
        """
        创建应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param obj: 创建应用权限定义表（{domain}.* namespace）参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppScopesParam) -> int:
        """
        更新应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param pk: 应用权限定义表（{domain}.* namespace） ID
        :param obj: 更新 应用权限定义表（{domain}.* namespace）参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除应用权限定义表（{domain}.* namespace）

        :param db: 数据库会话
        :param pks: 应用权限定义表（{domain}.* namespace） ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


app_scopes_dao: CRUDAppScopes = CRUDAppScopes(AppScopes)
