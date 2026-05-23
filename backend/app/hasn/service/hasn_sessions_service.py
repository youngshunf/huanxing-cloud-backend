from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_sessions import hasn_sessions_dao
from backend.app.hasn.model import HasnSessions
from backend.app.hasn.schema.hasn_sessions import CreateHasnSessionsParam, DeleteHasnSessionsParam, UpdateHasnSessionsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnSessionsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnSessions:
        """
        获取HASN 会话分层 - 逻辑会话

        :param db: 数据库会话
        :param pk: HASN 会话分层 - 逻辑会话 ID
        :return:
        """
        hasn_sessions = await hasn_sessions_dao.get(db, pk)
        if not hasn_sessions:
            raise errors.NotFoundError(msg='HASN 会话分层 - 逻辑会话不存在')
        return hasn_sessions

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN 会话分层 - 逻辑会话列表

        :param db: 数据库会话
        :return:
        """
        hasn_sessions_select = await hasn_sessions_dao.get_select()
        return await paging_data(db, hasn_sessions_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnSessions]:
        """
        获取所有HASN 会话分层 - 逻辑会话

        :param db: 数据库会话
        :return:
        """
        hasn_sessions_list = await hasn_sessions_dao.get_all(db)
        return hasn_sessions_list

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnSessionsParam) -> None:
        """
        创建HASN 会话分层 - 逻辑会话

        :param db: 数据库会话
        :param obj: 创建HASN 会话分层 - 逻辑会话参数
        :return:
        """
        await hasn_sessions_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnSessionsParam) -> int:
        """
        更新HASN 会话分层 - 逻辑会话

        :param db: 数据库会话
        :param pk: HASN 会话分层 - 逻辑会话 ID
        :param obj: 更新HASN 会话分层 - 逻辑会话参数
        :return:
        """
        count = await hasn_sessions_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnSessionsParam) -> int:
        """
        删除HASN 会话分层 - 逻辑会话

        :param db: 数据库会话
        :param obj: HASN 会话分层 - 逻辑会话 ID 列表
        :return:
        """
        count = await hasn_sessions_dao.delete(db, obj.pks)
        return count


hasn_sessions_service: HasnSessionsService = HasnSessionsService()
