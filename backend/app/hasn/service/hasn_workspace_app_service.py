from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_workspace_app import hasn_workspace_app_dao
from backend.app.hasn.model import HasnWorkspaceApp
from backend.app.hasn.schema.hasn_workspace_app import (
    CreateHasnWorkspaceAppParam,
    DeleteHasnWorkspaceAppParam,
    UpdateHasnWorkspaceAppParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnWorkspaceAppService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnWorkspaceApp:
        item = await hasn_workspace_app_dao.get(db, pk)
        if not item:
            raise errors.NotFoundError(msg='工作空间应用不存在')
        return item

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_workspace_app_dao.get_select())

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnWorkspaceApp]:
        return await hasn_workspace_app_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnWorkspaceAppParam) -> None:
        await hasn_workspace_app_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnWorkspaceAppParam) -> int:
        return await hasn_workspace_app_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnWorkspaceAppParam) -> int:
        return await hasn_workspace_app_dao.delete(db, obj.pks)


hasn_workspace_app_service: HasnWorkspaceAppService = HasnWorkspaceAppService()
