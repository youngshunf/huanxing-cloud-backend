from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_comments import hasn_comments_dao
from backend.app.hasn.model import HasnComments
from backend.app.hasn.schema.hasn_comments import CreateHasnCommentsParam, DeleteHasnCommentsParam, UpdateHasnCommentsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnCommentsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnComments:
        """
        获取社区评论

        :param db: 数据库会话
        :param pk: 社区评论 ID
        :return:
        """
        hasn_comments = await hasn_comments_dao.get(db, pk)
        if not hasn_comments:
            raise errors.NotFoundError(msg='社区评论不存在')
        return hasn_comments

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取社区评论列表

        :param db: 数据库会话
        :return:
        """
        hasn_comments_select = await hasn_comments_dao.get_select()
        return await paging_data(db, hasn_comments_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnComments]:
        """
        获取所有社区评论

        :param db: 数据库会话
        :return:
        """
        hasn_comments_list = await hasn_comments_dao.get_all(db)
        return hasn_comments_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnCommentsParam) -> None:
        """
        创建社区评论

        :param db: 数据库会话
        :param obj: 创建社区评论参数
        :return:
        """
        await hasn_comments_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnCommentsParam) -> int:
        """
        更新社区评论

        :param db: 数据库会话
        :param pk: 社区评论 ID
        :param obj: 更新社区评论参数
        :return:
        """
        count = await hasn_comments_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnCommentsParam) -> int:
        """
        删除社区评论

        :param db: 数据库会话
        :param obj: 社区评论 ID 列表
        :return:
        """
        count = await hasn_comments_dao.delete(db, obj.pks)
        return count


hasn_comments_service: HasnCommentsService = HasnCommentsService()
