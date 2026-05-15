from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppDataRecords
from backend.app.app_platform.schema.app_data_records import CreateAppDataRecordsParam, UpdateAppDataRecordsParam


class CRUDAppDataRecords(CRUDPlus[AppDataRecords]):
    async def get(self, db: AsyncSession, pk: int) -> AppDataRecords | None:
        """
        获取应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param pk: 应用数据记录表（JSONB 存储） ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取应用数据记录表（JSONB 存储）列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppDataRecords]:
        """
        获取所有应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppDataRecordsParam) -> AppDataRecords:
        """
        创建应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param obj: 创建应用数据记录表（JSONB 存储）参数
        :return:
        """
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppDataRecordsParam) -> int:
        """
        更新应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param pk: 应用数据记录表（JSONB 存储） ID
        :param obj: 更新 应用数据记录表（JSONB 存储）参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param pks: 应用数据记录表（JSONB 存储） ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_key(
        self,
        db: AsyncSession,
        owner_id: str,
        app_id: str,
        installation_id: str,
        resource_id: str,
        record_key: str,
    ) -> AppDataRecords | None:
        """
        根据隔离键和记录键获取数据

        :param db: 数据库会话
        :param owner_id: Owner ID
        :param app_id: App ID
        :param installation_id: Installation ID
        :param resource_id: Resource ID
        :param record_key: 记录键
        :return:
        """
        return await self.select_model_by_column(
            db,
            owner_id=owner_id,
            app_id=app_id,
            installation_id=installation_id,
            resource_id=resource_id,
            record_key=record_key,
        )

    async def list_by_resource(
        self,
        db: AsyncSession,
        owner_id: str,
        app_id: str,
        installation_id: str,
        resource_id: str,
        prefix: str | None = None,
    ) -> Sequence[AppDataRecords]:
        """
        列出指定 Resource 的所有数据

        :param db: 数据库会话
        :param owner_id: Owner ID
        :param app_id: App ID
        :param installation_id: Installation ID
        :param resource_id: Resource ID
        :param prefix: 记录键前缀（可选）
        :return:
        """
        if prefix:
            # TODO: 实现前缀查询
            pass
        return await self.select_models_by_column(
            db,
            owner_id=owner_id,
            app_id=app_id,
            installation_id=installation_id,
            resource_id=resource_id,
        )

    async def delete_by_key(
        self,
        db: AsyncSession,
        owner_id: str,
        app_id: str,
        installation_id: str,
        resource_id: str,
        record_key: str,
    ) -> int:
        """
        根据隔离键和记录键删除数据

        :param db: 数据库会话
        :param owner_id: Owner ID
        :param app_id: App ID
        :param installation_id: Installation ID
        :param resource_id: Resource ID
        :param record_key: 记录键
        :return: 删除的行数
        """
        return await self.delete_model_by_column(
            db,
            allow_multiple=False,
            owner_id=owner_id,
            app_id=app_id,
            installation_id=installation_id,
            resource_id=resource_id,
            record_key=record_key,
        )


app_data_records_dao: CRUDAppDataRecords = CRUDAppDataRecords(AppDataRecords)
