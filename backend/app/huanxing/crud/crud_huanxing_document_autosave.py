from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model import HuanxingDocumentAutosave
from backend.app.huanxing.schema.huanxing_document_autosave import CreateHuanxingDocumentAutosaveParam, UpdateHuanxingDocumentAutosaveParam


class CRUDHuanxingDocumentAutosave(CRUDPlus[HuanxingDocumentAutosave]):
    async def get(self, db: AsyncSession, pk: int) -> HuanxingDocumentAutosave | None:
        """
        获取文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param pk: 文档自动保存表（每文档每用户仅一条，UPSERT更新） ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取文档自动保存表（每文档每用户仅一条，UPSERT更新）列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HuanxingDocumentAutosave]:
        """
        获取所有文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHuanxingDocumentAutosaveParam) -> None:
        """
        创建文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param obj: 创建文档自动保存表（每文档每用户仅一条，UPSERT更新）参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHuanxingDocumentAutosaveParam) -> int:
        """
        更新文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param pk: 文档自动保存表（每文档每用户仅一条，UPSERT更新） ID
        :param obj: 更新 文档自动保存表（每文档每用户仅一条，UPSERT更新）参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除文档自动保存表（每文档每用户仅一条，UPSERT更新）

        :param db: 数据库会话
        :param pks: 文档自动保存表（每文档每用户仅一条，UPSERT更新） ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


huanxing_document_autosave_dao: CRUDHuanxingDocumentAutosave = CRUDHuanxingDocumentAutosave(HuanxingDocumentAutosave)
