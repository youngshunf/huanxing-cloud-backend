from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import PlatformScopes
from backend.app.app_platform.schema.platform_scopes import CreatePlatformScopesParam, UpdatePlatformScopesParam


class CRUDPlatformScopes(CRUDPlus[PlatformScopes]):
    async def get(self, db: AsyncSession, pk: int) -> PlatformScopes | None:
        """
        获取平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param pk: 平台权限定义表（hasn.* namespace） ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取平台权限定义表（hasn.* namespace）列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[PlatformScopes]:
        """
        获取所有平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreatePlatformScopesParam) -> None:
        """
        创建平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param obj: 创建平台权限定义表（hasn.* namespace）参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdatePlatformScopesParam) -> int:
        """
        更新平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param pk: 平台权限定义表（hasn.* namespace） ID
        :param obj: 更新 平台权限定义表（hasn.* namespace）参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除平台权限定义表（hasn.* namespace）

        :param db: 数据库会话
        :param pks: 平台权限定义表（hasn.* namespace） ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_scope(self, db: AsyncSession, scope: str) -> PlatformScopes | None:
        """
        根据 scope 获取平台权限定义

        :param db: 数据库会话
        :param scope: 权限标识
        :return:
        """
        return await self.select_model_by_column(db, scope=scope)


platform_scopes_dao: CRUDPlatformScopes = CRUDPlatformScopes(PlatformScopes)
