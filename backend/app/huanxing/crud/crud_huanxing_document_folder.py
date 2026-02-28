from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.huanxing.model.huanxing_document_folder import HuanxingDocumentFolder
from backend.app.huanxing.schema.huanxing_document_folder import CreateFolderParam, UpdateFolderParam


class CRUDHuanxingDocumentFolder(CRUDPlus[HuanxingDocumentFolder]):
    async def get(self, db: AsyncSession, pk: int) -> HuanxingDocumentFolder | None:
        return await self.select_model(db, pk)

    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> HuanxingDocumentFolder | None:
        return await self.select_model_by_column(db, uuid=uuid)

    async def get_select(self) -> Select:
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HuanxingDocumentFolder]:
        return await self.select_models(db)

    async def get_by_user(self, db: AsyncSession, user_id: int) -> Sequence[HuanxingDocumentFolder]:
        """获取用户的所有目录（不含已删除）"""
        return await self.select_models(db, user_id=user_id, deleted_at=None)

    async def get_children(self, db: AsyncSession, parent_id: int | None, user_id: int) -> Sequence[HuanxingDocumentFolder]:
        """获取某目录的直接子目录"""
        return await self.select_models(db, parent_id=parent_id, user_id=user_id, deleted_at=None)

    async def create(self, db: AsyncSession, obj: CreateFolderParam | dict) -> HuanxingDocumentFolder:
        if isinstance(obj, dict):
            ins = self.model(**obj)
            db.add(ins)
            await db.flush()
            return ins
        return await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateFolderParam | dict) -> int:
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


huanxing_document_folder_dao: CRUDHuanxingDocumentFolder = CRUDHuanxingDocumentFolder(HuanxingDocumentFolder)
