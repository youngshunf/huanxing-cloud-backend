from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_reviews import app_reviews_dao
from backend.app.app_platform.model import AppReviews
from backend.app.app_platform.schema.app_reviews import CreateAppReviewsParam, DeleteAppReviewsParam, UpdateAppReviewsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppReviewsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppReviews:
        """
        获取App 审核记录

        :param db: 数据库会话
        :param pk: App 审核记录 ID
        :return:
        """
        app_reviews = await app_reviews_dao.get(db, pk)
        if not app_reviews:
            raise errors.NotFoundError(msg='App 审核记录不存在')
        return app_reviews

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取App 审核记录列表

        :param db: 数据库会话
        :return:
        """
        app_reviews_select = await app_reviews_dao.get_select()
        return await paging_data(db, app_reviews_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppReviews]:
        """
        获取所有App 审核记录

        :param db: 数据库会话
        :return:
        """
        app_reviewss = await app_reviews_dao.get_all(db)
        return app_reviewss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppReviewsParam) -> None:
        """
        创建App 审核记录

        :param db: 数据库会话
        :param obj: 创建App 审核记录参数
        :return:
        """
        await app_reviews_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppReviewsParam) -> int:
        """
        更新App 审核记录

        :param db: 数据库会话
        :param pk: App 审核记录 ID
        :param obj: 更新App 审核记录参数
        :return:
        """
        count = await app_reviews_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppReviewsParam) -> int:
        """
        删除App 审核记录

        :param db: 数据库会话
        :param obj: App 审核记录 ID 列表
        :return:
        """
        count = await app_reviews_dao.delete(db, obj.pks)
        return count


app_reviews_service: AppReviewsService = AppReviewsService()
