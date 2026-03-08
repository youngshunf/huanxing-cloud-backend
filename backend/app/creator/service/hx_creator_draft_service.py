from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_draft import hx_creator_draft_dao
from backend.app.creator.model import HxCreatorDraft
from backend.app.creator.schema.hx_creator_draft import CreateHxCreatorDraftParam, DeleteHxCreatorDraftParam, UpdateHxCreatorDraftParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorDraftService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorDraft:
        """
        获取草稿箱

        :param db: 数据库会话
        :param pk: 草稿箱 ID
        :return:
        """
        hx_creator_draft = await hx_creator_draft_dao.get(db, pk)
        if not hx_creator_draft:
            raise errors.NotFoundError(msg='草稿箱不存在')
        return hx_creator_draft

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取草稿箱列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_draft_select = await hx_creator_draft_dao.get_select()
        return await paging_data(db, hx_creator_draft_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorDraft]:
        """
        获取所有草稿箱

        :param db: 数据库会话
        :return:
        """
        hx_creator_drafts = await hx_creator_draft_dao.get_all(db)
        return hx_creator_drafts

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorDraftParam) -> None:
        """
        创建草稿箱

        :param db: 数据库会话
        :param obj: 创建草稿箱参数
        :return:
        """
        await hx_creator_draft_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorDraftParam) -> int:
        """
        更新草稿箱

        :param db: 数据库会话
        :param pk: 草稿箱 ID
        :param obj: 更新草稿箱参数
        :return:
        """
        count = await hx_creator_draft_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorDraftParam) -> int:
        """
        删除草稿箱

        :param db: 数据库会话
        :param obj: 草稿箱 ID 列表
        :return:
        """
        count = await hx_creator_draft_dao.delete(db, obj.pks)
        return count


hx_creator_draft_service: HxCreatorDraftService = HxCreatorDraftService()
