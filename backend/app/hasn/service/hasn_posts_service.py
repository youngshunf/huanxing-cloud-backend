from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_posts import hasn_posts_dao
from backend.app.hasn.model import HasnPosts
from backend.app.hasn.schema.hasn_posts import CreateHasnPostsParam, DeleteHasnPostsParam, UpdateHasnPostsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnPostsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnPosts:
        """
        获取社区帖子

        :param db: 数据库会话
        :param pk: 社区帖子 ID
        :return:
        """
        hasn_posts = await hasn_posts_dao.get(db, pk)
        if not hasn_posts:
            raise errors.NotFoundError(msg='社区帖子不存在')
        return hasn_posts

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取社区帖子列表

        :param db: 数据库会话
        :return:
        """
        hasn_posts_select = await hasn_posts_dao.get_select()
        return await paging_data(db, hasn_posts_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnPosts]:
        """
        获取所有社区帖子

        :param db: 数据库会话
        :return:
        """
        hasn_posts_list = await hasn_posts_dao.get_all(db)
        return hasn_posts_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnPostsParam) -> None:
        """
        创建社区帖子

        :param db: 数据库会话
        :param obj: 创建社区帖子参数
        :return:
        """
        await hasn_posts_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnPostsParam) -> int:
        """
        更新社区帖子

        :param db: 数据库会话
        :param pk: 社区帖子 ID
        :param obj: 更新社区帖子参数
        :return:
        """
        count = await hasn_posts_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnPostsParam) -> int:
        """
        删除社区帖子

        :param db: 数据库会话
        :param obj: 社区帖子 ID 列表
        :return:
        """
        count = await hasn_posts_dao.delete(db, obj.pks)
        return count


hasn_posts_service: HasnPostsService = HasnPostsService()
