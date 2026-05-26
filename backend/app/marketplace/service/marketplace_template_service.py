from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.marketplace.crud.crud_marketplace_template import marketplace_template_dao
from backend.app.marketplace.model import MarketplaceTemplate
from backend.app.marketplace.schema.marketplace_template import CreateMarketplaceTemplateParam, DeleteMarketplaceTemplateParam, UpdateMarketplaceTemplateParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class MarketplaceTemplateService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> MarketplaceTemplate:
        """
        获取技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param pk: 技能市场模板表（Agent模板/技能包/SOP包） ID
        :return:
        """
        marketplace_template = await marketplace_template_dao.get(db, pk)
        if not marketplace_template:
            raise errors.NotFoundError(msg='技能市场模板表（Agent模板/技能包/SOP包）不存在')
        return marketplace_template

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取技能市场模板表（Agent模板/技能包/SOP包）列表

        :param db: 数据库会话
        :return:
        """
        marketplace_template_select = await marketplace_template_dao.get_select()
        return await paging_data(db, marketplace_template_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[MarketplaceTemplate]:
        """
        获取所有技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :return:
        """
        marketplace_template_list = await marketplace_template_dao.get_all(db)
        return marketplace_template_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateMarketplaceTemplateParam) -> None:
        """
        创建技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param obj: 创建技能市场模板表（Agent模板/技能包/SOP包）参数
        :return:
        """
        await marketplace_template_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateMarketplaceTemplateParam) -> int:
        """
        更新技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param pk: 技能市场模板表（Agent模板/技能包/SOP包） ID
        :param obj: 更新技能市场模板表（Agent模板/技能包/SOP包）参数
        :return:
        """
        count = await marketplace_template_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteMarketplaceTemplateParam) -> int:
        """
        删除技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param obj: 技能市场模板表（Agent模板/技能包/SOP包） ID 列表
        :return:
        """
        count = await marketplace_template_dao.delete(db, obj.pks)
        return count


marketplace_template_service: MarketplaceTemplateService = MarketplaceTemplateService()
