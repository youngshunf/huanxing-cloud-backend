from typing import Sequence, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.marketplace.model import MarketplaceTemplate
from backend.app.marketplace.schema.marketplace_template import CreateMarketplaceTemplateParam, UpdateMarketplaceTemplateParam


class CRUDMarketplaceTemplate(CRUDPlus[MarketplaceTemplate]):
    async def get(self, db: AsyncSession, pk: int) -> MarketplaceTemplate | None:
        """
        获取技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param pk: 技能市场模板表（Agent模板/技能包/SOP包） ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取技能市场模板表（Agent模板/技能包/SOP包）列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[MarketplaceTemplate]:
        """
        获取所有技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateMarketplaceTemplateParam) -> None:
        """
        创建技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param obj: 创建技能市场模板表（Agent模板/技能包/SOP包）参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateMarketplaceTemplateParam) -> int:
        """
        更新技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param pk: 技能市场模板表（Agent模板/技能包/SOP包） ID
        :param obj: 更新 技能市场模板表（Agent模板/技能包/SOP包）参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除技能市场模板表（Agent模板/技能包/SOP包）

        :param db: 数据库会话
        :param pks: 技能市场模板表（Agent模板/技能包/SOP包） ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)

    async def get_by_id(self, db: AsyncSession, template_id: str) -> MarketplaceTemplate | None:
        """
        根据模板ID获取模板

        :param db: 数据库会话
        :param template_id: 模板ID
        :return:
        """
        return await self.select_model_by_column(db, template_id=template_id)

    async def get_select_public(
        self,
        category: Optional[str] = None,
        tags: Optional[str] = None,
        pricing_type: Optional[str] = None,
        is_official: Optional[bool] = None,
    ) -> Select:
        """
        获取公开模板列表的查询表达式

        :param category: 分类筛选
        :param tags: 标签筛选
        :param pricing_type: 定价类型筛选
        :param is_official: 是否官方筛选
        :return: 查询表达式
        """
        # 构建基础查询 - 只返回公开的模板
        stmt = select(MarketplaceTemplate).where(MarketplaceTemplate.is_private == False)

        # 添加筛选条件
        if category:
            stmt = stmt.where(MarketplaceTemplate.category == category)
        if tags:
            stmt = stmt.where(MarketplaceTemplate.tags.contains(tags))
        if pricing_type:
            stmt = stmt.where(MarketplaceTemplate.pricing_type == pricing_type)
        if is_official is not None:
            stmt = stmt.where(MarketplaceTemplate.is_official == is_official)

        # 排序：官方优先，然后按下载量降序
        stmt = stmt.order_by(
            MarketplaceTemplate.is_official.desc(),
            MarketplaceTemplate.download_count.desc(),
            MarketplaceTemplate.id.desc(),
        )

        return stmt

    async def increment_download_count(self, db: AsyncSession, template_id: str) -> None:
        """
        增加模板下载次数

        :param db: 数据库会话
        :param template_id: 模板ID
        """
        from sqlalchemy import update
        stmt = (
            update(MarketplaceTemplate)
            .where(MarketplaceTemplate.template_id == template_id)
            .values(download_count=MarketplaceTemplate.download_count + 1)
        )
        await db.execute(stmt)


marketplace_template_dao: CRUDMarketplaceTemplate = CRUDMarketplaceTemplate(MarketplaceTemplate)
