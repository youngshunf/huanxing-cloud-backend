"""HASN Agent管理端 Service"""
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.admin.hasn_agents import hasn_agents_admin_dao
from backend.app.hasn_core.model import HasnAgent
from backend.app.hasn_core.schema.admin.hasn_agents import CreateHasnAgentParam, DeleteHasnAgentParam, UpdateHasnAgentParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnAgentAdminService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: str) -> HasnAgent:
        obj = await hasn_agents_admin_dao.get(db, pk)
        if not obj:
            raise errors.NotFoundError(msg='Agent不存在')
        return obj

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await hasn_agents_admin_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnAgentParam) -> None:
        await hasn_agents_admin_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: str, obj: UpdateHasnAgentParam) -> int:
        return await hasn_agents_admin_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnAgentParam) -> int:
        return await hasn_agents_admin_dao.delete(db, obj.pks)


hasn_agents_admin_service: HasnAgentAdminService = HasnAgentAdminService()
