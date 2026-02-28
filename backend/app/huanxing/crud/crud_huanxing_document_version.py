from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model import HuanxingDocumentVersion
from backend.app.huanxing.schema.huanxing_document_version import CreateHuanxingDocumentVersionParam, UpdateHuanxingDocumentVersionParam


class CRUDHuanxingDocumentVersion(CRUDPlus[HuanxingDocumentVersion]):
    async def get(self, db: AsyncSession, pk: int) -> HuanxingDocumentVersion | None:
        """
        获取文档版本历史

        :param db: 数据库会话
        :param pk: 文档版本历史 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取文档版本历史列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HuanxingDocumentVersion]:
        """
        获取所有文档版本历史

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHuanxingDocumentVersionParam | dict) -> HuanxingDocumentVersion:
        """
        创建文档版本历史

        :param db: 数据库会话
        :param obj: 创建文档版本历史参数（Pydantic模型或dict）
        :return: 创建的版本对象
        """
        if isinstance(obj, dict):
            ins = self.model(**obj)
            db.add(ins)
            await db.flush()
            return ins
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHuanxingDocumentVersionParam) -> int:
        """
        更新文档版本历史

        :param db: 数据库会话
        :param pk: 文档版本历史 ID
        :param obj: 更新 文档版本历史参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除文档版本历史

        :param db: 数据库会话
        :param pks: 文档版本历史 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


huanxing_document_version_dao: CRUDHuanxingDocumentVersion = CRUDHuanxingDocumentVersion(HuanxingDocumentVersion)
