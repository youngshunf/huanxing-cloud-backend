from collections.abc import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppTools
from backend.app.app_platform.schema.app_tools import CreateAppToolsParam, UpdateAppToolsParam


class CRUDAppTools(CRUDPlus[AppTools]):
    async def get(self, db: AsyncSession, pk: int) -> AppTools | None:
        """
        获取App Tool 定义

        :param db: 数据库会话
        :param pk: App Tool 定义 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取App Tool 定义列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppTools]:
        """
        获取所有App Tool 定义

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppToolsParam) -> None:
        """
        创建App Tool 定义

        :param db: 数据库会话
        :param obj: 创建App Tool 定义参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppToolsParam) -> int:
        """
        更新App Tool 定义

        :param db: 数据库会话
        :param pk: App Tool 定义 ID
        :param obj: 更新 App Tool 定义参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除App Tool 定义

        :param db: 数据库会话
        :param pks: App Tool 定义 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_tool_id(self, db: AsyncSession, tool_id: str) -> AppTools | None:
        """
        根据 tool_id 获取 Tool

        :param db: 数据库会话
        :param tool_id: Tool ID
        :return:
        """
        return await self.select_model_by_column(db, tool_id=tool_id)

    async def get_by_app_id(self, db: AsyncSession, app_id: str) -> list[AppTools]:
        """
        根据 app_id 获取该 App 的所有 Tool

        :param db: 数据库会话
        :param app_id: App ID
        :return:
        """
        return list(await self.select_models(db, app_id=app_id))

    async def get_by_version_id(self, db: AsyncSession, version_id: str) -> list[AppTools]:
        """
        根据 version_id 获取该版本的所有 Tool

        :param db: 数据库会话
        :param version_id: 版本 ID
        :return:
        """
        return list(await self.select_models(db, version_id=version_id))


app_tools_dao: CRUDAppTools = CRUDAppTools(AppTools)
