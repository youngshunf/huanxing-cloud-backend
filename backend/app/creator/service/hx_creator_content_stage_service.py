from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_content_stage import hx_creator_content_stage_dao
from backend.app.creator.model import HxCreatorContentStage
from backend.app.creator.schema.hx_creator_content_stage import CreateHxCreatorContentStageParam, DeleteHxCreatorContentStageParam, UpdateHxCreatorContentStageParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorContentStageService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorContentStage:
        """
        获取内容阶段产出

        :param db: 数据库会话
        :param pk: 内容阶段产出 ID
        :return:
        """
        hx_creator_content_stage = await hx_creator_content_stage_dao.get(db, pk)
        if not hx_creator_content_stage:
            raise errors.NotFoundError(msg='内容阶段产出不存在')
        return hx_creator_content_stage

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取内容阶段产出列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_content_stage_select = await hx_creator_content_stage_dao.get_select()
        return await paging_data(db, hx_creator_content_stage_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorContentStage]:
        """
        获取所有内容阶段产出

        :param db: 数据库会话
        :return:
        """
        hx_creator_content_stages = await hx_creator_content_stage_dao.get_all(db)
        return hx_creator_content_stages

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorContentStageParam) -> None:
        """
        创建内容阶段产出

        :param db: 数据库会话
        :param obj: 创建内容阶段产出参数
        :return:
        """
        await hx_creator_content_stage_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorContentStageParam) -> int:
        """
        更新内容阶段产出

        :param db: 数据库会话
        :param pk: 内容阶段产出 ID
        :param obj: 更新内容阶段产出参数
        :return:
        """
        count = await hx_creator_content_stage_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorContentStageParam) -> int:
        """
        删除内容阶段产出

        :param db: 数据库会话
        :param obj: 内容阶段产出 ID 列表
        :return:
        """
        count = await hx_creator_content_stage_dao.delete(db, obj.pks)
        return count


hx_creator_content_stage_service: HxCreatorContentStageService = HxCreatorContentStageService()
