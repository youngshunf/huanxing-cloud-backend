from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_likes import hasn_likes_dao
from backend.app.hasn.model import HasnLikes
from backend.app.hasn.schema.hasn_likes import CreateHasnLikesParam, DeleteHasnLikesParam, UpdateHasnLikesParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnLikesService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnLikes:
        """
        获取社区点赞

        :param db: 数据库会话
        :param pk: 社区点赞 ID
        :return:
        """
        hasn_likes = await hasn_likes_dao.get(db, pk)
        if not hasn_likes:
            raise errors.NotFoundError(msg='社区点赞不存在')
        return hasn_likes

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取社区点赞列表

        :param db: 数据库会话
        :return:
        """
        hasn_likes_select = await hasn_likes_dao.get_select()
        return await paging_data(db, hasn_likes_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnLikes]:
        """
        获取所有社区点赞

        :param db: 数据库会话
        :return:
        """
        hasn_likes_list = await hasn_likes_dao.get_all(db)
        return hasn_likes_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnLikesParam) -> None:
        """
        创建社区点赞

        :param db: 数据库会话
        :param obj: 创建社区点赞参数
        :return:
        """
        await hasn_likes_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnLikesParam) -> int:
        """
        更新社区点赞

        :param db: 数据库会话
        :param pk: 社区点赞 ID
        :param obj: 更新社区点赞参数
        :return:
        """
        count = await hasn_likes_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnLikesParam) -> int:
        """
        删除社区点赞

        :param db: 数据库会话
        :param obj: 社区点赞 ID 列表
        :return:
        """
        count = await hasn_likes_dao.delete(db, obj.pks)
        return count


hasn_likes_service: HasnLikesService = HasnLikesService()
