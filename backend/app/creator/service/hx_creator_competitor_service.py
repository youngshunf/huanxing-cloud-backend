from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.creator.crud.crud_hx_creator_competitor import hx_creator_competitor_dao
from backend.app.creator.model import HxCreatorCompetitor
from backend.app.creator.schema.hx_creator_competitor import CreateHxCreatorCompetitorParam, DeleteHxCreatorCompetitorParam, UpdateHxCreatorCompetitorParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HxCreatorCompetitorService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HxCreatorCompetitor:
        """
        获取竞品账号

        :param db: 数据库会话
        :param pk: 竞品账号 ID
        :return:
        """
        hx_creator_competitor = await hx_creator_competitor_dao.get(db, pk)
        if not hx_creator_competitor:
            raise errors.NotFoundError(msg='竞品账号不存在')
        return hx_creator_competitor

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取竞品账号列表

        :param db: 数据库会话
        :return:
        """
        hx_creator_competitor_select = await hx_creator_competitor_dao.get_select()
        return await paging_data(db, hx_creator_competitor_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HxCreatorCompetitor]:
        """
        获取所有竞品账号

        :param db: 数据库会话
        :return:
        """
        hx_creator_competitors = await hx_creator_competitor_dao.get_all(db)
        return hx_creator_competitors

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHxCreatorCompetitorParam) -> None:
        """
        创建竞品账号

        :param db: 数据库会话
        :param obj: 创建竞品账号参数
        :return:
        """
        await hx_creator_competitor_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHxCreatorCompetitorParam) -> int:
        """
        更新竞品账号

        :param db: 数据库会话
        :param pk: 竞品账号 ID
        :param obj: 更新竞品账号参数
        :return:
        """
        count = await hx_creator_competitor_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHxCreatorCompetitorParam) -> int:
        """
        删除竞品账号

        :param db: 数据库会话
        :param obj: 竞品账号 ID 列表
        :return:
        """
        count = await hx_creator_competitor_dao.delete(db, obj.pks)
        return count


hx_creator_competitor_service: HxCreatorCompetitorService = HxCreatorCompetitorService()
