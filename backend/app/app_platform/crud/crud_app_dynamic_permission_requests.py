from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppDynamicPermissionRequests
from backend.app.app_platform.schema.app_dynamic_permission_requests import CreateAppDynamicPermissionRequestsParam, UpdateAppDynamicPermissionRequestsParam


class CRUDAppDynamicPermissionRequests(CRUDPlus[AppDynamicPermissionRequests]):
    async def get(self, db: AsyncSession, pk: int) -> AppDynamicPermissionRequests | None:
        """
        获取动态权限请求

        :param db: 数据库会话
        :param pk: 动态权限请求 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取动态权限请求列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppDynamicPermissionRequests]:
        """
        获取所有动态权限请求

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppDynamicPermissionRequestsParam) -> None:
        """
        创建动态权限请求

        :param db: 数据库会话
        :param obj: 创建动态权限请求参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppDynamicPermissionRequestsParam) -> int:
        """
        更新动态权限请求

        :param db: 数据库会话
        :param pk: 动态权限请求 ID
        :param obj: 更新 动态权限请求参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除动态权限请求

        :param db: 数据库会话
        :param pks: 动态权限请求 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


app_dynamic_permission_requests_dao: CRUDAppDynamicPermissionRequests = CRUDAppDynamicPermissionRequests(AppDynamicPermissionRequests)
