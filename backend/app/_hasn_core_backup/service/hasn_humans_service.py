from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.crud_hasn_humans import hasn_humans_dao
from backend.app.hasn_core.model import HasnHumans
from backend.app.hasn_core.schema.hasn_humans import CreateHasnHumansParam, DeleteHasnHumansParam, UpdateHasnHumansParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnHumansService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnHumans:
        """
        获取HASN Human 用户

        :param db: 数据库会话
        :param pk: HASN Human 用户 ID
        :return:
        """
        hasn_humans = await hasn_humans_dao.get(db, pk)
        if not hasn_humans:
            raise errors.NotFoundError(msg='HASN Human 用户不存在')
        return hasn_humans

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN Human 用户列表

        :param db: 数据库会话
        :return:
        """
        hasn_humans_select = await hasn_humans_dao.get_select()
        return await paging_data(db, hasn_humans_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnHumans]:
        """
        获取所有HASN Human 用户

        :param db: 数据库会话
        :return:
        """
        hasn_humanss = await hasn_humans_dao.get_all(db)
        return hasn_humanss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnHumansParam) -> None:
        """
        创建HASN Human 用户

        :param db: 数据库会话
        :param obj: 创建HASN Human 用户参数
        :return:
        """
        await hasn_humans_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnHumansParam) -> int:
        """
        更新HASN Human 用户

        :param db: 数据库会话
        :param pk: HASN Human 用户 ID
        :param obj: 更新HASN Human 用户参数
        :return:
        """
        count = await hasn_humans_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnHumansParam) -> int:
        """
        删除HASN Human 用户

        :param db: 数据库会话
        :param obj: HASN Human 用户 ID 列表
        :return:
        """
        count = await hasn_humans_dao.delete(db, obj.pks)
        return count


hasn_humans_service: HasnHumansService = HasnHumansService()
