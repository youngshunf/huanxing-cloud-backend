from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_data_records import app_data_records_dao
from backend.app.app_platform.model import AppDataRecords
from backend.app.app_platform.schema.app_data_records import CreateAppDataRecordsParam, DeleteAppDataRecordsParam, UpdateAppDataRecordsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppDataRecordsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppDataRecords:
        """
        获取应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param pk: 应用数据记录表（JSONB 存储） ID
        :return:
        """
        app_data_records = await app_data_records_dao.get(db, pk)
        if not app_data_records:
            raise errors.NotFoundError(msg='应用数据记录表（JSONB 存储）不存在')
        return app_data_records

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取应用数据记录表（JSONB 存储）列表

        :param db: 数据库会话
        :return:
        """
        app_data_records_select = await app_data_records_dao.get_select()
        return await paging_data(db, app_data_records_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppDataRecords]:
        """
        获取所有应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :return:
        """
        app_data_recordss = await app_data_records_dao.get_all(db)
        return app_data_recordss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppDataRecordsParam) -> None:
        """
        创建应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param obj: 创建应用数据记录表（JSONB 存储）参数
        :return:
        """
        await app_data_records_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppDataRecordsParam) -> int:
        """
        更新应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param pk: 应用数据记录表（JSONB 存储） ID
        :param obj: 更新应用数据记录表（JSONB 存储）参数
        :return:
        """
        count = await app_data_records_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppDataRecordsParam) -> int:
        """
        删除应用数据记录表（JSONB 存储）

        :param db: 数据库会话
        :param obj: 应用数据记录表（JSONB 存储） ID 列表
        :return:
        """
        count = await app_data_records_dao.delete(db, obj.pks)
        return count


app_data_records_service: AppDataRecordsService = AppDataRecordsService()
