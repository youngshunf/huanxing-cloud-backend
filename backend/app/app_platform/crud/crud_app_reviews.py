from typing import Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.app_platform.model import AppReviews
from backend.app.app_platform.schema.app_reviews import CreateAppReviewsParam, UpdateAppReviewsParam


class CRUDAppReviews(CRUDPlus[AppReviews]):
    async def get(self, db: AsyncSession, pk: int) -> AppReviews | None:
        """
        获取App 审核记录

        :param db: 数据库会话
        :param pk: App 审核记录 ID
        :return:
        """
        return await self.select_model(db, pk)

    async def get_select(self) -> Select:
        """获取App 审核记录列表查询表达式"""
        return await self.select_order('id', 'desc')

    async def get_all(self, db: AsyncSession) -> Sequence[AppReviews]:
        """
        获取所有App 审核记录

        :param db: 数据库会话
        :return:
        """
        return await self.select_models(db)

    async def create(self, db: AsyncSession, obj: CreateAppReviewsParam) -> None:
        """
        创建App 审核记录

        :param db: 数据库会话
        :param obj: 创建App 审核记录参数
        :return:
        """
        await self.create_model(db, obj)

    async def update(self, db: AsyncSession, pk: int, obj: UpdateAppReviewsParam) -> int:
        """
        更新App 审核记录

        :param db: 数据库会话
        :param pk: App 审核记录 ID
        :param obj: 更新 App 审核记录参数
        :return:
        """
        return await self.update_model(db, pk, obj)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除App 审核记录

        :param db: 数据库会话
        :param pks: App 审核记录 ID 列表
        :return:
        """
        return await self.delete_model_by_column(db, allow_multiple=True, id__in=pks)


app_reviews_dao: CRUDAppReviews = CRUDAppReviews(AppReviews)
