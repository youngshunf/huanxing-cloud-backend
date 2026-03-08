"""HASN 通知管理端 Service"""
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn_core.crud.admin.hasn_notifications import hasn_notifications_admin_dao
from backend.app.hasn_core.model import HasnNotification
from backend.app.hasn_core.schema.admin.hasn_notifications import CreateHasnNotificationParam, DeleteHasnNotificationParam, UpdateHasnNotificationParam
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnNotificationAdminService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnNotification:
        obj = await hasn_notifications_admin_dao.get(db, pk)
        if not obj:
            raise errors.NotFoundError(msg='通知不存在')
        return obj

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        select_stmt = await hasn_notifications_admin_dao.get_select()
        return await paging_data(db, select_stmt)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnNotificationParam) -> None:
        await hasn_notifications_admin_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnNotificationParam) -> int:
        return await hasn_notifications_admin_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnNotificationParam) -> int:
        return await hasn_notifications_admin_dao.delete(db, obj.pks)


hasn_notifications_admin_service: HasnNotificationAdminService = HasnNotificationAdminService()
