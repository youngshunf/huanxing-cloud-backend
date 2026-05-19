from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_enterprise_membership import hasn_enterprise_membership_dao
from backend.app.hasn.model import HasnEnterpriseMembership
from backend.app.hasn.schema.hasn_enterprise_membership import (
    CreateHasnEnterpriseMembershipParam,
    DeleteHasnEnterpriseMembershipParam,
    UpdateHasnEnterpriseMembershipParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnEnterpriseMembershipService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnEnterpriseMembership:
        item = await hasn_enterprise_membership_dao.get(db, pk)
        if not item:
            raise errors.NotFoundError(msg='企业成员关系不存在')
        return item

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_enterprise_membership_dao.get_select())

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnEnterpriseMembership]:
        return await hasn_enterprise_membership_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnEnterpriseMembershipParam) -> None:
        await hasn_enterprise_membership_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnEnterpriseMembershipParam) -> int:
        return await hasn_enterprise_membership_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnEnterpriseMembershipParam) -> int:
        return await hasn_enterprise_membership_dao.delete(db, obj.pks)


hasn_enterprise_membership_service: HasnEnterpriseMembershipService = HasnEnterpriseMembershipService()
