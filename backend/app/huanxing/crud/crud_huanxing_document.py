from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model import HuanxingDocument
from backend.app.huanxing.schema.huanxing_document import CreateHuanxingDocumentParam, UpdateHuanxingDocumentParam


class CRUDHuanxingDocument(CRUDPlus[HuanxingDocument]):
    async def get(self, db: AsyncSession, pk: int) -> HuanxingDocument | None:
        """
        获取唤星文档

        :param db: 数据库会话
        :param pk: 唤星文档 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取唤星文档列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HuanxingDocument]:
        """
        获取所有唤星文档

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHuanxingDocumentParam | dict) -> HuanxingDocument:
        """
        创建唤星文档

        :param db: 数据库会话
        :param obj: 创建唤星文档参数（Pydantic模型或dict）
        :return: 创建的文档对象
        """
        if isinstance(obj, dict):
            ins = self.model(**obj)
            db.add(ins)
            await db.flush()
            return ins
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHuanxingDocumentParam) -> int:
        """
        更新唤星文档

        :param db: 数据库会话
        :param pk: 唤星文档 ID
        :param obj: 更新 唤星文档参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除唤星文档

        :param db: 数据库会话
        :param pks: 唤星文档 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


huanxing_document_dao: CRUDHuanxingDocument = CRUDHuanxingDocument(HuanxingDocument)
