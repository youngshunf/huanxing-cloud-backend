from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.hasn.crud.crud_hasn_enterprise_invite_code import hasn_enterprise_invite_code_dao
from backend.app.hasn.model import HasnEnterpriseInviteCode
from backend.app.hasn.schema.hasn_enterprise_invite_code import (
    CreateHasnEnterpriseInviteCodeParam,
    DeleteHasnEnterpriseInviteCodeParam,
    UpdateHasnEnterpriseInviteCodeParam,
)
from backend.common.exception import errors
from backend.common.pagination import paging_data


class HasnEnterpriseInviteCodeService:
    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> HasnEnterpriseInviteCode:
        item = await hasn_enterprise_invite_code_dao.get(db, pk)
        if not item:
            raise errors.NotFoundError(msg='企业邀请码不存在')
        return item

    @staticmethod
    async def get_list(db: AsyncSession) -> dict[str, Any]:
        return await paging_data(db, await hasn_enterprise_invite_code_dao.get_select())

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[HasnEnterpriseInviteCode]:
        return await hasn_enterprise_invite_code_dao.get_all(db)

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateHasnEnterpriseInviteCodeParam) -> None:
        await hasn_enterprise_invite_code_dao.create(db, obj)

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateHasnEnterpriseInviteCodeParam) -> int:
        return await hasn_enterprise_invite_code_dao.update(db, pk, obj)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteHasnEnterpriseInviteCodeParam) -> int:
        return await hasn_enterprise_invite_code_dao.delete(db, obj.pks)


hasn_enterprise_invite_code_service: HasnEnterpriseInviteCodeService = HasnEnterpriseInviteCodeService()
