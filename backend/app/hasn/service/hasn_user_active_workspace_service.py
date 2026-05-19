from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_user_active_workspace import hasn_user_active_workspace_dao
from backend.app.hasn.model import HasnUserActiveWorkspace
from backend.app.hasn.schema.hasn_user_active_workspace import (
    CreateHasnUserActiveWorkspaceParam,
    DeleteHasnUserActiveWorkspaceParam,
    UpdateHasnUserActiveWorkspaceParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnUserActiveWorkspaceService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnUserActiveWorkspace:
        item = await hasn_user_active_workspace_dao.get(db, pk)
        if not item:
            raise errors.NotFoundError(msg='活跃工作区不存在')
        return item

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_user_active_workspace_dao.get_select())

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnUserActiveWorkspace]:
        return await hasn_user_active_workspace_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnUserActiveWorkspaceParam) -> None:
        await hasn_user_active_workspace_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnUserActiveWorkspaceParam) -> int:
        return await hasn_user_active_workspace_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnUserActiveWorkspaceParam) -> int:
        return await hasn_user_active_workspace_dao.delete(db, obj.pks)


hasn_user_active_workspace_service: HasnUserActiveWorkspaceService = HasnUserActiveWorkspaceService()
