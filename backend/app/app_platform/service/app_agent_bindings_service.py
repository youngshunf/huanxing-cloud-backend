from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.app_platform.crud.crud_app_agent_bindings import app_agent_bindings_dao
from backend.app.app_platform.model import AppAgentBindings
from backend.app.app_platform.schema.app_agent_bindings import CreateAppAgentBindingsParam, DeleteAppAgentBindingsParam, UpdateAppAgentBindingsParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class AppAgentBindingsService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> AppAgentBindings:
        """
        获取Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param pk: Installation 绑定的 Agent 列 ID
        :return:
        """
        app_agent_bindings = await app_agent_bindings_dao.get(db, pk)
        if not app_agent_bindings:
            raise errors.NotFoundError(msg='Installation 绑定的 Agent 列不存在')
        return app_agent_bindings

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        """
        获取Installation 绑定的 Agent 列列表

        :param db: 数据库会话
        :return:
        """
        app_agent_bindings_select = await app_agent_bindings_dao.get_select()
        return await paging_data(db, app_agent_bindings_select)

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AppAgentBindings]:
        """
        获取所有Installation 绑定的 Agent 列

        :param db: 数据库会话
        :return:
        """
        app_agent_bindingss = await app_agent_bindings_dao.get_all(db)
        return app_agent_bindingss

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAppAgentBindingsParam) -> None:
        """
        创建Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param obj: 创建Installation 绑定的 Agent 列参数
        :return:
        """
        await app_agent_bindings_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAppAgentBindingsParam) -> int:
        """
        更新Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param pk: Installation 绑定的 Agent 列 ID
        :param obj: 更新Installation 绑定的 Agent 列参数
        :return:
        """
        count = await app_agent_bindings_dao.update(db, pk, obj)
        return count

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAppAgentBindingsParam) -> int:
        """
        删除Installation 绑定的 Agent 列

        :param db: 数据库会话
        :param obj: Installation 绑定的 Agent 列 ID 列表
        :return:
        """
        count = await app_agent_bindings_dao.delete(db, obj.pks)
        return count


app_agent_bindings_service: AppAgentBindingsService = AppAgentBindingsService()
