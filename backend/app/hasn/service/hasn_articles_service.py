from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_articles import hasn_articles_dao
from backend.app.hasn.model import HasnArticles
from backend.app.hasn.schema.hasn_articles import CreateHasnArticlesParam, DeleteHasnArticlesParam, UpdateHasnArticlesParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnArticlesService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnArticles:
        """
        获取社区文章

        :param db: 数据库会话
        :param pk: 社区文章 ID
        :return:
        """
        hasn_articles = await hasn_articles_dao.get(db, pk)
        if not hasn_articles:
            raise errors.NotFoundError(msg='社区文章不存在')
        return hasn_articles

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取社区文章列表

        :param db: 数据库会话
        :return:
        """
        hasn_articles_select = await hasn_articles_dao.get_select()
        return await paging_data(db, hasn_articles_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnArticles]:
        """
        获取所有社区文章

        :param db: 数据库会话
        :return:
        """
        hasn_articles_list = await hasn_articles_dao.get_all(db)
        return hasn_articles_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnArticlesParam) -> None:
        """
        创建社区文章

        :param db: 数据库会话
        :param obj: 创建社区文章参数
        :return:
        """
        await hasn_articles_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnArticlesParam) -> int:
        """
        更新社区文章

        :param db: 数据库会话
        :param pk: 社区文章 ID
        :param obj: 更新社区文章参数
        :return:
        """
        count = await hasn_articles_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnArticlesParam) -> int:
        """
        删除社区文章

        :param db: 数据库会话
        :param obj: 社区文章 ID 列表
        :return:
        """
        count = await hasn_articles_dao.delete(db, obj.pks)
        return count


hasn_articles_service: HasnArticlesService = HasnArticlesService()
