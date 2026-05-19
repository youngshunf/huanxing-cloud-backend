from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_enterprise import hasn_enterprise_dao
from backend.app.hasn.model import HasnEnterprise
from backend.app.hasn.schema.hasn_enterprise import (
    CreateHasnEnterpriseParam,
    DeleteHasnEnterpriseParam,
    UpdateHasnEnterpriseParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnEnterpriseService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnEnterprise:
        item = await hasn_enterprise_dao.get(db, pk)
        if not item:
            raise errors.NotFoundError(msg='企业不存在')
        return item

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_enterprise_dao.get_select())

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnEnterprise]:
        return await hasn_enterprise_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnEnterpriseParam) -> None:
        await hasn_enterprise_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnEnterpriseParam) -> int:
        return await hasn_enterprise_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnEnterpriseParam) -> int:
        return await hasn_enterprise_dao.delete(db, obj.pks)


hasn_enterprise_service: HasnEnterpriseService = HasnEnterpriseService()
