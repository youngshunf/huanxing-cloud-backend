from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_viral_pattern import hx_creator_viral_pattern_dao
from backend.app.creator.model import HxCreatorViralPattern
from backend.app.creator.schema.hx_creator_viral_pattern import CreateHxCreatorViralPatternParam, DeleteHxCreatorViralPatternParam, UpdateHxCreatorViralPatternParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorViralPatternService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorViralPattern:
        """
        获取爆款模式库

        :param db: 数据库会话
        :param pk: 爆款模式库 ID
        :return:
        """
        hx_creator_viral_pattern = await hx_creator_viral_pattern_dao.get(db, pk)
        if not hx_creator_viral_pattern:
            raise errors.NotFoundError(msg='爆款模式库不存在')
        return hx_creator_viral_pattern

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取爆款模式库列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_viral_pattern_select = await hx_creator_viral_pattern_dao.get_select()
        return await paging_data(db, hx_creator_viral_pattern_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorViralPattern]:
        """
        获取所有爆款模式库

        :param db: 数据库会话
        :return:
        """
        hx_creator_viral_patterns = await hx_creator_viral_pattern_dao.get_all(db)
        return hx_creator_viral_patterns

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorViralPatternParam) -> None:
        """
        创建爆款模式库

        :param db: 数据库会话
        :param obj: 创建爆款模式库参数
        :return:
        """
        await hx_creator_viral_pattern_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorViralPatternParam) -> int:
        """
        更新爆款模式库

        :param db: 数据库会话
        :param pk: 爆款模式库 ID
        :param obj: 更新爆款模式库参数
        :return:
        """
        count = await hx_creator_viral_pattern_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorViralPatternParam) -> int:
        """
        删除爆款模式库

        :param db: 数据库会话
        :param obj: 爆款模式库 ID 列表
        :return:
        """
        count = await hx_creator_viral_pattern_dao.delete(db, obj.pks)
        return count


hx_creator_viral_pattern_service: HxCreatorViralPatternService = HxCreatorViralPatternService()
