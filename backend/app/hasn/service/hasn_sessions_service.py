from typing import Any, Sequence
from datetime import datetime

from sqlalchemy import select
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

    @staticmethod
    async def upsert(*, db: AsyncSession, session_data: dict) -> HasnSessions:
        """
        创建或更新 Session（幂等操作）

        :param db: 数据库会话
        :param session_data: Session 数据
        :return:
        """
        session_id = session_data.get('session_id')

        # 查询是否已存在
        stmt = select(HasnSessions).where(HasnSessions.session_id == session_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # 更新现有 Session
            for key, value in session_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_time = datetime.now()
            await db.flush()
            return existing
        else:
            # 创建新 Session
            new_session = HasnSessions(**session_data)
            db.add(new_session)
            await db.flush()
            return new_session

    @staticmethod
    async def update_summary(*, db: AsyncSession, session_id: str, summary_data: dict) -> HasnSessions:
        """
        更新 Session 摘要

        :param db: 数据库会话
        :param session_id: Session ID
        :param summary_data: 摘要数据
        :return:
        """
        stmt = select(HasnSessions).where(HasnSessions.session_id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise errors.NotFoundError(msg='Session 不存在')

        # 更新摘要和最后消息时间
        session.summary_checkpoint_json = summary_data.get('summary_checkpoint_json', session.summary_checkpoint_json)
        session.last_message_at = summary_data.get('last_message_at', session.last_message_at)
        session.updated_time = datetime.now()

        await db.flush()
        return session

    @staticmethod
    async def close_session(*, db: AsyncSession, session_id: str, close_data: dict) -> HasnSessions:
        """
        关闭 Session

        :param db: 数据库会话
        :param session_id: Session ID
        :param close_data: 关闭数据
        :return:
        """
        stmt = select(HasnSessions).where(HasnSessions.session_id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise errors.NotFoundError(msg='Session 不存在')

        # 更新状态和关闭时间
        session.session_status = close_data.get('session_status', 'completed')
        session.closed_at = datetime.now()
        session.updated_time = datetime.now()

        await db.flush()
        return session

    @staticmethod
    async def get_by_session_id(*, db: AsyncSession, session_id: str) -> HasnSessions:
        """
        根据 session_id 获取 Session

        :param db: 数据库会话
        :param session_id: Session ID
        :return:
        """
        stmt = select(HasnSessions).where(HasnSessions.session_id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise errors.NotFoundError(msg='Session 不存在')

        return session


hasn_sessions_service: HasnSessionsService = HasnSessionsService()
