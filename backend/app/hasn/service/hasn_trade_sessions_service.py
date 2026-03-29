from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_trade_sessions import hasn_trade_sessions_dao
from backend.app.hasn.model import HasnTradeSessions
from backend.app.hasn.schema.hasn_trade_sessions import CreateHasnTradeSessionsParam, DeleteHasnTradeSessionsParam, UpdateHasnTradeSessionsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnTradeSessionsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnTradeSessions:
        """
        获取HASN 交易会话

        :param db: 数据库会话
        :param pk: HASN 交易会话 ID
        :return:
        """
        hasn_trade_sessions = await hasn_trade_sessions_dao.get(db, pk)
        if not hasn_trade_sessions:
            raise errors.NotFoundError(msg='HASN 交易会话不存在')
        return hasn_trade_sessions

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取HASN 交易会话列表

        :param db: 数据库会话
        :return:
        """
        hasn_trade_sessions_select = await hasn_trade_sessions_dao.get_select()
        return await paging_data(db, hasn_trade_sessions_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnTradeSessions]:
        """
        获取所有HASN 交易会话

        :param db: 数据库会话
        :return:
        """
        hasn_trade_sessionss = await hasn_trade_sessions_dao.get_all(db)
        return hasn_trade_sessionss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnTradeSessionsParam) -> None:
        """
        创建HASN 交易会话

        :param db: 数据库会话
        :param obj: 创建HASN 交易会话参数
        :return:
        """
        await hasn_trade_sessions_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnTradeSessionsParam) -> int:
        """
        更新HASN 交易会话

        :param db: 数据库会话
        :param pk: HASN 交易会话 ID
        :param obj: 更新HASN 交易会话参数
        :return:
        """
        count = await hasn_trade_sessions_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnTradeSessionsParam) -> int:
        """
        删除HASN 交易会话

        :param db: 数据库会话
        :param obj: HASN 交易会话 ID 列表
        :return:
        """
        count = await hasn_trade_sessions_dao.delete(db, obj.pks)
        return count


hasn_trade_sessions_service: HasnTradeSessionsService = HasnTradeSessionsService()
