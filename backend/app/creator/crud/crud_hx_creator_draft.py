from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.creator.model import HxCreatorDraft
from backend.app.creator.schema.hx_creator_draft import CreateHxCreatorDraftParam, UpdateHxCreatorDraftParam


class CRUDHxCreatorDraft(CRUDPlus[HxCreatorDraft]):
    async def get(self, db: AsyncSession, pk: int) -> HxCreatorDraft | None:
        """
        获取草稿箱

        :param db: 数据库会话
        :param pk: 草稿箱 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取草稿箱列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[HxCreatorDraft]:
        """
        获取所有草稿箱

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateHxCreatorDraftParam) -> None:
        """
        创建草稿箱

        :param db: 数据库会话
        :param obj: 创建草稿箱参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateHxCreatorDraftParam) -> int:
        """
        更新草稿箱

        :param db: 数据库会话
        :param pk: 草稿箱 ID
        :param obj: 更新 草稿箱参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除草稿箱

        :param db: 数据库会话
        :param pks: 草稿箱 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


hx_creator_draft_dao: CRUDHxCreatorDraft = CRUDHxCreatorDraft(HxCreatorDraft)
