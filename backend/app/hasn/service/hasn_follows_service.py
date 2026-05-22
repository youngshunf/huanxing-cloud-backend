from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_follows import hasn_follows_dao
from backend.app.hasn.model import HasnFollows
from backend.app.hasn.schema.hasn_follows import CreateHasnFollowsParam, DeleteHasnFollowsParam, UpdateHasnFollowsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnFollowsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnFollows:
        """
        获取社区关注

        :param db: 数据库会话
        :param pk: 社区关注 ID
        :return:
        """
        hasn_follows = await hasn_follows_dao.get(db, pk)
        if not hasn_follows:
            raise errors.NotFoundError(msg='社区关注不存在')
        return hasn_follows

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取社区关注列表

        :param db: 数据库会话
        :return:
        """
        hasn_follows_select = await hasn_follows_dao.get_select()
        return await paging_data(db, hasn_follows_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnFollows]:
        """
        获取所有社区关注

        :param db: 数据库会话
        :return:
        """
        hasn_follows_list = await hasn_follows_dao.get_all(db)
        return hasn_follows_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnFollowsParam) -> None:
        """
        创建社区关注

        :param db: 数据库会话
        :param obj: 创建社区关注参数
        :return:
        """
        await hasn_follows_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnFollowsParam) -> int:
        """
        更新社区关注

        :param db: 数据库会话
        :param pk: 社区关注 ID
        :param obj: 更新社区关注参数
        :return:
        """
        count = await hasn_follows_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnFollowsParam) -> int:
        """
        删除社区关注

        :param db: 数据库会话
        :param obj: 社区关注 ID 列表
        :return:
        """
        count = await hasn_follows_dao.delete(db, obj.pks)
        return count


hasn_follows_service: HasnFollowsService = HasnFollowsService()
