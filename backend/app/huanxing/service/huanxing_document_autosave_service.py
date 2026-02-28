from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.huanxing.crud.crud_huanxing_document_autosave import huanxing_document_autosave_dao
from backend.app.huanxing.model import HuanxingDocumentAutosave
from backend.app.huanxing.schema.huanxing_document_autosave import CreateHuanxingDocumentAutosaveParam, DeleteHuanxingDocumentAutosaveParam, UpdateHuanxingDocumentAutosaveParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HuanxingDocumentAutosaveService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HuanxingDocumentAutosave:
        """
        获取文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param pk: 文档自动保存表（每文档每用户仅一条，UPSERT更新） ID
        :return:
        """
        huanxing_document_autosave = await huanxing_document_autosave_dao.get(db, pk)
        if not huanxing_document_autosave:
            raise errors.NotFoundError(msg='文档自动保存表（每文档每用户仅一条，UPSERT更新）不存在')
        return huanxing_document_autosave

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取文档自动保存表（每文档每用户仅一条，UPSERT更新）列表

        :param db: 数据库会话
        :return:
        """
        huanxing_document_autosave_select = await huanxing_document_autosave_dao.get_select()
        return await paging_data(db, huanxing_document_autosave_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HuanxingDocumentAutosave]:
        """
        获取所有文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :return:
        """
        huanxing_document_autosaves = await huanxing_document_autosave_dao.get_all(db)
        return huanxing_document_autosaves

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHuanxingDocumentAutosaveParam) -> None:
        """
        创建文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param obj: 创建文档自动保存表（每文档每用户仅一条，UPSERT更新）参数
        :return:
        """
        await huanxing_document_autosave_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHuanxingDocumentAutosaveParam) -> int:
        """
        更新文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param pk: 文档自动保存表（每文档每用户仅一条，UPSERT更新） ID
        :param obj: 更新文档自动保存表（每文档每用户仅一条，UPSERT更新）参数
        :return:
        """
        count = await huanxing_document_autosave_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHuanxingDocumentAutosaveParam) -> int:
        """
        删除文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param obj: 文档自动保存表（每文档每用户仅一条，UPSERT更新） ID 列表
        :return:
        """
        count = await huanxing_document_autosave_dao.delete(db, obj.pks)
        return count


huanxing_document_autosave_service: HuanxingDocumentAutosaveService = HuanxingDocumentAutosaveService()
